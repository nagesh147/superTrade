from __future__ import annotations

from typing import Iterable, List

from app.schemas.market import Candle, HACandle


def build_heikin_ashi(candles: Iterable[Candle]) -> List[HACandle]:
    candles = list(candles)
    if not candles:
        return []
    out: List[HACandle] = []
    for i, c in enumerate(candles):
        ha_close = (c.open + c.high + c.low + c.close) / 4.0
        if i == 0:
            ha_open = (c.open + c.close) / 2.0
        else:
            prev = out[-1]
            ha_open = (prev.open + prev.close) / 2.0
        ha_high = max(c.high, ha_open, ha_close)
        ha_low = min(c.low, ha_open, ha_close)
        out.append(HACandle(ts=c.ts, open=ha_open, high=ha_high, low=ha_low, close=ha_close))
    return out
