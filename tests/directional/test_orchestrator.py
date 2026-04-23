from __future__ import annotations

from app.engines.directional.orchestrator import DirectionalOrchestrator


def test_orchestrator_returns_actionable_state(
    bullish_4h_candles,
    bullish_1h_candles,
    bullish_15m_pullback_candles,
    healthy_chain,
    account_snapshot,
):
    result = DirectionalOrchestrator().run_cycle(
        symbol='BTCUSD',
        candles_4h=bullish_4h_candles,
        candles_1h=bullish_1h_candles,
        candles_15m=bullish_15m_pullback_candles,
        chain=healthy_chain,
        iv_rank=45.0,
        account=account_snapshot,
        event_blocked=False,
    )
    assert result.status in {'READY', 'WAIT', 'NO_TRADE', 'BLOCKED', 'NO_SIZE', 'HOLD'}
    if result.status == 'READY':
        assert result.plan is not None
        assert result.plan.qty >= 1
