from __future__ import annotations

from dataclasses import dataclass

from app.core.enums import Direction, ExitReason
from app.schemas.directional import ExitDecision, PositionSnapshot


@dataclass(slots=True)
class MonitorConfig:
    max_premium_dd_pct: float = 0.50
    hard_exit_dte: int = 3
    time_stop_bars: int = 4
    min_progress_r: float = 0.35
    de_risk_r: float = 1.5


class MonitorEngine:
    def __init__(self, config: MonitorConfig | None = None) -> None:
        self.config = config or MonitorConfig()

    def evaluate(self, position: PositionSnapshot, st_fast_value: float) -> ExitDecision:
        if position.direction == Direction.BULLISH and position.current_underlying_price < st_fast_value:
            return ExitDecision(True, ExitReason.THESIS_STOP, False, ["underlying below fast ST"]) 
        if position.direction == Direction.BEARISH and position.current_underlying_price > st_fast_value:
            return ExitDecision(True, ExitReason.THESIS_STOP, False, ["underlying above fast ST"]) 
        drawdown = 1.0 - (position.current_option_value / max(position.entry_option_cost, 1e-9))
        if drawdown >= self.config.max_premium_dd_pct:
            return ExitDecision(True, ExitReason.FINANCIAL_STOP, False, ["premium drawdown threshold breached"]) 
        if position.dte_remaining <= self.config.hard_exit_dte:
            return ExitDecision(True, ExitReason.EXPIRY_EXIT, False, ["hard DTE exit"]) 
        if position.bars_in_trade >= self.config.time_stop_bars and position.realized_r_multiple < self.config.min_progress_r:
            return ExitDecision(True, ExitReason.TIME_STOP, False, ["insufficient progress"]) 
        if not position.reduced_once and position.realized_r_multiple >= self.config.de_risk_r:
            return ExitDecision(False, ExitReason.PROFIT_TARGET, True, ["take partial profits"]) 
        return ExitDecision(False, ExitReason.NONE, False, [])
