from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from app.core.enums import Direction, TriggerMode
from app.engines.directional.scoring import continuation_score, pullback_score
from app.engines.indicators.atr import atr
from app.engines.indicators.stats import clamp
from app.schemas.directional import ExecutionTrigger, SetupEvent
from app.schemas.market import Candle


@dataclass(slots=True)
class ExecutionConfig:
    retest_tolerance_pct: float = 0.003
    continuation_max_extension_atr: float = 1.5


class ExecutionEngine:
    def __init__(self, config: ExecutionConfig | None = None) -> None:
        self.config = config or ExecutionConfig()

    def evaluate_pullback(self, setup: SetupEvent, candles_15m: Sequence[Candle], st_fast_value: float) -> ExecutionTrigger:
        if len(candles_15m) < 20:
            return ExecutionTrigger(mode=TriggerMode.WAIT, score=0.0, trigger_price=None, invalidation_price=None, reasons=["insufficient 15m candles"])
        last = candles_15m[-1]
        recent_atr = max(atr(candles_15m[-20:], 14)[-1], 1e-9)
        if setup.direction == Direction.BULLISH:
            touch_distance = abs(last.low - st_fast_value) / max(st_fast_value, 1e-9)
            p1 = clamp(1.0 - touch_distance / self.config.retest_tolerance_pct)
            p2 = 1.0 if last.close > st_fast_value else 0.0
            rejection = max(0.0, min(1.0, (min(last.open, last.close) - last.low) / max(last.high - last.low, 1e-9)))
        else:
            touch_distance = abs(last.high - st_fast_value) / max(st_fast_value, 1e-9)
            p1 = clamp(1.0 - touch_distance / self.config.retest_tolerance_pct)
            p2 = 1.0 if last.close < st_fast_value else 0.0
            rejection = max(0.0, min(1.0, (last.high - max(last.open, last.close)) / max(last.high - last.low, 1e-9)))
        p3 = rejection
        avg_volume = sum(c.volume for c in candles_15m[-20:]) / 20.0
        p4 = clamp(last.volume / max(avg_volume, 1e-9))
        extension = abs(last.close - st_fast_value) / recent_atr
        p5 = clamp(extension / self.config.continuation_max_extension_atr)
        score = pullback_score(p1, p2, p3, p4, p5)
        mode = TriggerMode.PULLBACK if score >= 72 else TriggerMode.WAIT
        return ExecutionTrigger(mode=mode, score=score, trigger_price=last.close if mode == TriggerMode.PULLBACK else None, invalidation_price=st_fast_value, reasons=[])

    def evaluate_continuation(self, setup: SetupEvent, candles_15m: Sequence[Candle], regime_strength: float) -> ExecutionTrigger:
        if len(candles_15m) < 20:
            return ExecutionTrigger(mode=TriggerMode.WAIT, score=0.0, trigger_price=None, invalidation_price=None, reasons=["insufficient 15m candles"])
        last = candles_15m[-1]
        prev_window = candles_15m[-6:-1]
        recent_atr = max(atr(candles_15m[-20:], 14)[-1], 1e-9)
        if setup.direction == Direction.BULLISH:
            prior_extreme = max(c.high for c in prev_window)
            c1 = 1.0 if last.close > prior_extreme else 0.0
        else:
            prior_extreme = min(c.low for c in prev_window)
            c1 = 1.0 if last.close < prior_extreme else 0.0
        c2 = clamp((last.high - last.low) / recent_atr)
        avg_volume = sum(c.volume for c in candles_15m[-20:]) / 20.0
        c3 = clamp(last.volume / max(avg_volume, 1e-9))
        extension = abs(last.close - prev_window[-1].close) / recent_atr
        c4 = clamp(extension / self.config.continuation_max_extension_atr)
        c5 = clamp(abs(regime_strength) / 100.0)
        score = continuation_score(c1, c2, c3, c4, c5)
        mode = TriggerMode.CONTINUATION if score >= 75 else TriggerMode.WAIT
        invalidation = prev_window[-1].low if setup.direction == Direction.BULLISH else prev_window[-1].high
        return ExecutionTrigger(mode=mode, score=score, trigger_price=last.close if mode == TriggerMode.CONTINUATION else None, invalidation_price=invalidation, reasons=[])
