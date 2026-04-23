from __future__ import annotations

from datetime import datetime, timezone

from app.core.enums import Direction, ExitReason, StructureType
from app.engines.directional.monitor_engine import MonitorEngine
from app.engines.directional.sizing_engine import SizingEngine
from app.schemas.directional import PositionSnapshot, StructureDecision


def test_sizing_uses_min_of_caps(account_snapshot):
    decision = StructureDecision(StructureType.NAKED_CALL, 80, 70, 60, 20, ['ok'])
    sizing = SizingEngine().compute(decision, account_snapshot, unit_cost=2.5, unit_margin=2.0)
    assert sizing.final_qty > 0
    assert sizing.final_qty == min(sizing.qty_by_cost, sizing.qty_by_margin, sizing.qty_by_portfolio)


def test_monitor_thesis_stop_triggers():
    position = PositionSnapshot(
        entry_time=datetime.now(timezone.utc),
        direction=Direction.BULLISH,
        structure=StructureType.NAKED_CALL,
        entry_underlying_price=80000,
        entry_option_cost=2.0,
        current_option_value=1.8,
        current_underlying_price=79000,
        bars_in_trade=1,
        dte_remaining=10,
    )
    decision = MonitorEngine().evaluate(position, st_fast_value=79500)
    assert decision.should_exit
    assert decision.reason == ExitReason.THESIS_STOP


def test_monitor_profit_reduce_only():
    position = PositionSnapshot(
        entry_time=datetime.now(timezone.utc),
        direction=Direction.BULLISH,
        structure=StructureType.NAKED_CALL,
        entry_underlying_price=80000,
        entry_option_cost=2.0,
        current_option_value=5.0,
        current_underlying_price=81000,
        bars_in_trade=2,
        dte_remaining=10,
        realized_r_multiple=1.6,
        reduced_once=False,
    )
    decision = MonitorEngine().evaluate(position, st_fast_value=79000)
    assert not decision.should_exit
    assert decision.reduce_only
