from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List

from app.engines.indicators.atr import atr
from app.schemas.market import Candle, HACandle


@dataclass(slots=True)
class SuperTrendPoint:
    value: float
    direction: str


def compute_supertrend(candles: Iterable[Candle | HACandle], period: int, multiplier: float) -> List[SuperTrendPoint]:
    candles = list(candles)
    if not candles:
        return []
    atr_values = atr(candles, period)
    hl2 = [(c.high + c.low) / 2.0 for c in candles]
    upper_basic = [m + multiplier * a for m, a in zip(hl2, atr_values)]
    lower_basic = [m - multiplier * a for m, a in zip(hl2, atr_values)]

    final_upper = [upper_basic[0]]
    final_lower = [lower_basic[0]]
    points: List[SuperTrendPoint] = [SuperTrendPoint(value=lower_basic[0], direction="green")]
    direction = "green"

    for i in range(1, len(candles)):
        prev_close = candles[i - 1].close
        fu = upper_basic[i] if upper_basic[i] < final_upper[-1] or prev_close > final_upper[-1] else final_upper[-1]
        fl = lower_basic[i] if lower_basic[i] > final_lower[-1] or prev_close < final_lower[-1] else final_lower[-1]
        final_upper.append(fu)
        final_lower.append(fl)

        close = candles[i].close
        if close > final_upper[i - 1]:
            direction = "green"
        elif close < final_lower[i - 1]:
            direction = "red"
        else:
            direction = points[-1].direction

        value = final_lower[i] if direction == "green" else final_upper[i]
        points.append(SuperTrendPoint(value=value, direction=direction))
    return points
