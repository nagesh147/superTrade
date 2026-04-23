from __future__ import annotations

from app.engines.indicators.heikin_ashi import build_heikin_ashi
from app.engines.indicators.ema import ema
from app.engines.indicators.atr import atr
from app.engines.indicators.supertrend import compute_supertrend
from tests.conftest import make_candles


def test_heikin_ashi_builds_same_length():
    candles = make_candles(100, [1, 2, -1, 3], minutes=60)
    ha = build_heikin_ashi(candles)
    assert len(ha) == len(candles)
    assert ha[0].open == (candles[0].open + candles[0].close) / 2


def test_ema_monotonic_on_rising_series():
    out = ema([1, 2, 3, 4, 5], 3)
    assert len(out) == 5
    assert out[-1] > out[0]


def test_atr_positive():
    candles = make_candles(100, [2, -1, 4, -2, 3], minutes=60)
    values = atr(candles, 3)
    assert all(v >= 0 for v in values)
    assert values[-1] > 0


def test_supertrend_direction_on_bullish_series():
    candles = make_candles(100, [2]*30, minutes=60)
    st = compute_supertrend(candles, 7, 3)
    assert st[-1].direction == 'green'
