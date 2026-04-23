from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from app.core.enums import Direction
from app.engines.indicators.atr import atr
from app.engines.indicators.ema import ema
from app.engines.indicators.stats import clamp, mean, signed_unit
from app.engines.directional.scoring import macro_regime_score
from app.schemas.directional import MacroRegime
from app.schemas.market import Candle


@dataclass(slots=True)
class RegimeConfig:
    ema_period: int = 50
    breakout_lookback: int = 20
    atr_period: int = 14


class RegimeEngine:
    def __init__(self, config: RegimeConfig | None = None) -> None:
        self.config = config or RegimeConfig()

    def evaluate_4h(self, symbol: str, candles: Sequence[Candle]) -> MacroRegime:
        if len(candles) < max(self.config.ema_period, self.config.breakout_lookback) + 2:
            raise ValueError("insufficient candles for macro regime")
        closes = [c.close for c in candles]
        ema50 = ema(closes, self.config.ema_period)
        atr_values = atr(candles, self.config.atr_period)
        last = candles[-1]
        prev = candles[-2]
        last_ema = ema50[-1]
        f1 = 1.0 if last.close > last_ema else -1.0
        ema_slope = ema50[-1] - ema50[-5]
        slope_scale = max(last_ema * 0.01, 1e-9)
        f2 = signed_unit(ema_slope, slope_scale)
        recent_atr = mean(atr_values[-5:])
        base_atr = max(mean(atr_values[-20:-5]), 1e-9)
        f3 = signed_unit(recent_atr - base_atr, base_atr)
        window = candles[-self.config.breakout_lookback:]
        highest = max(c.high for c in window)
        lowest = min(c.low for c in window)
        range_span = max(highest - lowest, 1e-9)
        range_pos = ((last.close - lowest) / range_span) * 2 - 1
        f4 = max(-1.0, min(1.0, range_pos))
        body = last.close - last.open
        rng = max(last.high - last.low, 1e-9)
        body_dom = body / rng
        f5 = max(-1.0, min(1.0, body_dom))
        score = macro_regime_score(f1, f2, f3, f4, f5)
        if score >= 35:
            regime = Direction.BULLISH
        elif score <= -35:
            regime = Direction.BEARISH
        else:
            regime = Direction.NEUTRAL
        quality = clamp(abs(score) / 100.0)
        return MacroRegime(
            ts=last.ts,
            symbol=symbol,
            regime=regime,
            score=score,
            features={"f1": f1, "f2": f2, "f3": f3, "f4": f4, "f5": f5},
            quality=quality,
        )
