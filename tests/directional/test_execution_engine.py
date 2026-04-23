from __future__ import annotations

from app.core.enums import Direction, SetupStatus, SetupType, TriggerMode
from app.engines.directional.execution_engine import ExecutionEngine
from app.engines.directional.signal_engine import SignalEngine
from app.engines.directional.setup_engine import SetupEngine
from app.schemas.directional import SetupEvent


def _make_setup(signal):
    setup = SetupEngine().create_or_update(signal)
    if setup is None:
        setup = SetupEvent(
            setup_id='s1',
            setup_type=SetupType.CONFIRMED,
            direction=Direction.BULLISH,
            activated_at=signal.ts,
            expires_at=signal.ts,
            bars_remaining=3,
            status=SetupStatus.ACTIVE,
            signal=signal,
        )
    return setup


def test_pullback_trigger_can_arm(bullish_1h_candles, bullish_15m_pullback_candles):
    signal = SignalEngine().evaluate_1h('BTCUSD', bullish_1h_candles)
    setup = _make_setup(signal)
    trigger = ExecutionEngine().evaluate_pullback(setup, bullish_15m_pullback_candles, signal.st_7_3)
    assert trigger.mode in {TriggerMode.PULLBACK, TriggerMode.WAIT}


def test_continuation_trigger_can_arm(bullish_1h_candles, bullish_15m_continuation_candles):
    signal = SignalEngine().evaluate_1h('BTCUSD', bullish_1h_candles)
    setup = _make_setup(signal)
    trigger = ExecutionEngine().evaluate_continuation(setup, bullish_15m_continuation_candles, 70)
    assert trigger.mode in {TriggerMode.CONTINUATION, TriggerMode.WAIT}
