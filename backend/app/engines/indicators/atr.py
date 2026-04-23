from __future__ import annotations

from typing import Iterable, List

from app.schemas.market import Candle, HACandle


def true_ranges(candles: Iterable[Candle | HACandle]) -> List[float]:
    candles = list(candles)
    if not candles:
        return []
    trs = [candles[0].high - candles[0].low]
    for prev, cur in zip(candles, candles[1:]):
        trs.append(max(
            cur.high - cur.low,
            abs(cur.high - prev.close),
            abs(cur.low - prev.close),
        ))
    return trs


def rma(values: Iterable[float], period: int) -> List[float]:
    values = list(values)
    if not values:
        return []
    if period <= 0:
        raise ValueError("period must be > 0")
    out = [values[0]]
    alpha = 1.0 / period
    for v in values[1:]:
        out.append(alpha * v + (1.0 - alpha) * out[-1])
    return out


def atr(candles: Iterable[Candle | HACandle], period: int) -> List[float]:
    return rma(true_ranges(candles), period)
