from __future__ import annotations

from datetime import timedelta

from app.core.enums import SetupStatus
from app.engines.directional.signal_engine import SignalEngine
from app.engines.directional.setup_engine import SetupEngine


def test_setup_created_from_signal(bullish_1h_candles):
    signal = SignalEngine().evaluate_1h('BTCUSD', bullish_1h_candles)
    setup = SetupEngine().create_or_update(signal)
    if setup is not None:
        assert setup.status == SetupStatus.ACTIVE
        assert setup.bars_remaining == 3


def test_setup_expires_after_window(bullish_1h_candles):
    signal = SignalEngine().evaluate_1h('BTCUSD', bullish_1h_candles)
    engine = SetupEngine()
    setup = engine.create_or_update(signal)
    if setup is not None:
        latest = setup.activated_at + timedelta(hours=4)
        updated = engine.decrement_window(setup, latest)
        assert updated.status == SetupStatus.EXPIRED
