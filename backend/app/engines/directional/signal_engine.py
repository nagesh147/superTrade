from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from app.core.enums import Direction
from app.engines.directional.scoring import directional_signal_score
from app.engines.indicators.atr import atr
from app.engines.indicators.heikin_ashi import build_heikin_ashi
from app.engines.indicators.stats import clamp
from app.engines.indicators.supertrend import compute_supertrend
from app.schemas.directional import DirectionalSignal
from app.schemas.market import Candle


@dataclass(slots=True)
class SignalConfig:
    fast_period: int = 7
    fast_multiplier: float = 3.0
    mid_period: int = 14
    mid_multiplier: float = 2.0
    slow_period: int = 21
    slow_multiplier: float = 1.0


class SignalEngine:
    def __init__(self, config: SignalConfig | None = None) -> None:
        self.config = config or SignalConfig()

    def evaluate_1h(self, symbol: str, real_candles: Sequence[Candle]) -> DirectionalSignal:
        if len(real_candles) < self.config.slow_period + 5:
            raise ValueError("insufficient candles for signal")
        ha = build_heikin_ashi(real_candles)
        fast = compute_supertrend(ha, self.config.fast_period, self.config.fast_multiplier)
        mid = compute_supertrend(ha, self.config.mid_period, self.config.mid_multiplier)
        slow = compute_supertrend(ha, self.config.slow_period, self.config.slow_multiplier)
        last = ha[-1]
        prev_idx = -2

        dirs = [fast[-1].direction, mid[-1].direction, slow[-1].direction]
        prev_dirs = [fast[prev_idx].direction, mid[prev_idx].direction, slow[prev_idx].direction]
        alignment_strength = sum(d == "green" for d in dirs) if all(d == "green" for d in dirs) else sum(d == "red" for d in dirs) if all(d == "red" for d in dirs) else sum(1 for d in dirs if d == max(set(dirs), key=dirs.count))
        all_green = all(d == "green" for d in dirs)
        all_red = all(d == "red" for d in dirs)
        prev_all_green = all(d == "green" for d in prev_dirs)
        prev_all_red = all(d == "red" for d in prev_dirs)
        green_arrow = all_green and not prev_all_green
        red_arrow = all_red and not prev_all_red

        atr_values = atr(ha, 14)
        last_atr = max(atr_values[-1], 1e-9)
        g1 = alignment_strength / 3.0
        g2_long = 1.0 if green_arrow else 0.0
        g2_short = 1.0 if red_arrow else 0.0
        g3 = clamp(abs(last.close - last.open) / last_atr)
        st_zone = fast[-1].value
        g4 = max(-1.0, min(1.0, (last.close - st_zone) / last_atr))
        dist_fast_mid = abs(fast[-1].value - mid[-1].value)
        dist_mid_slow = abs(mid[-1].value - slow[-1].value)
        g5 = clamp((dist_fast_mid + dist_mid_slow) / (2.0 * last_atr))
        score_long = directional_signal_score(g1, g2_long, g3, g4, g5, bullish=True)
        score_short = directional_signal_score(g1, g2_short, g3, g4, g5, bullish=False)

        if all_green:
            direction = Direction.BULLISH
        elif all_red:
            direction = Direction.BEARISH
        else:
            direction = Direction.NEUTRAL

        return DirectionalSignal(
            ts=real_candles[-1].ts,
            symbol=symbol,
            direction_state=direction,
            alignment_strength=alignment_strength if direction != Direction.NEUTRAL else 0,
            green_arrow=green_arrow,
            red_arrow=red_arrow,
            score_long=score_long,
            score_short=score_short,
            st_7_3=fast[-1].value,
            st_14_2=mid[-1].value,
            st_21_1=slow[-1].value,
            features={"g1": g1, "g3": g3, "g4": g4, "g5": g5},
        )
