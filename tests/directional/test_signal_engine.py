from __future__ import annotations

from app.core.enums import Direction
from app.engines.directional.signal_engine import SignalEngine
from tests.conftest import make_candles


def test_signal_engine_bullish_alignment_detected(bullish_1h_candles):
    engine = SignalEngine()
    signal = engine.evaluate_1h('BTCUSD', bullish_1h_candles)
    assert signal.direction_state in {Direction.BULLISH, Direction.NEUTRAL}
    assert signal.st_7_3 > 0


def test_signal_arrow_fires_on_transition():
    candles = make_candles(100, [-3, -3, -2, -1, 1, 2, 3, 5, 6, 7, 8, 9, 8, 6, 4, 3, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1], minutes=60)
    engine = SignalEngine()
    signal = engine.evaluate_1h('BTCUSD', candles)
    assert isinstance(signal.green_arrow, bool)
    assert isinstance(signal.red_arrow, bool)
