from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, List

from app.core.enums import Direction, SetupStatus, SetupType, StructureType, TriggerMode, ExitReason
from app.schemas.market import OptionQuote


@dataclass(slots=True)
class MacroRegime:
    ts: datetime
    symbol: str
    regime: Direction
    score: float
    features: Dict[str, float]
    quality: float


@dataclass(slots=True)
class DirectionalSignal:
    ts: datetime
    symbol: str
    direction_state: Direction
    alignment_strength: int
    green_arrow: bool
    red_arrow: bool
    score_long: float
    score_short: float
    st_7_3: float
    st_14_2: float
    st_21_1: float
    features: Dict[str, float] = field(default_factory=dict)


@dataclass(slots=True)
class SetupEvent:
    setup_id: str
    setup_type: SetupType
    direction: Direction
    activated_at: datetime
    expires_at: datetime
    bars_remaining: int
    status: SetupStatus
    signal: DirectionalSignal


@dataclass(slots=True)
class FilterDecision:
    allowed: bool
    reasons: List[str]
    preferred_structure_family: str
    dte_pass: bool
    vol_pass: bool
    macro_pass: bool
    event_pass: bool
    liquidity_pass: bool


@dataclass(slots=True)
class ExecutionTrigger:
    mode: TriggerMode
    score: float
    trigger_price: Optional[float]
    invalidation_price: Optional[float]
    reasons: List[str] = field(default_factory=list)


@dataclass(slots=True)
class OptionTranslation:
    direction: Direction
    required_delta_min: float
    required_delta_max: float
    preferred_dte_min: int
    preferred_dte_max: int
    expected_move_pct: float
    expected_bars_to_work: int
    theta_budget_pct: float
    breakeven_move_pct: float
    preferred_structure_family: str


@dataclass(slots=True)
class ContractHealth:
    symbol: str
    score: float
    veto_reasons: List[str] = field(default_factory=list)
    spread_pct: float = 0.0
    mark_mid_dev: float = 0.0
    responsiveness_score: float = 0.0
    quote_quality_score: float = 0.0


@dataclass(slots=True)
class StructureDecision:
    chosen_structure: StructureType
    score_naked: float
    score_debit: float
    score_credit: float
    score_no_trade: float
    rationale: List[str]
    legs: List[OptionQuote] = field(default_factory=list)


@dataclass(slots=True)
class SizingDecision:
    max_risk_usd: float
    unit_cost: float
    unit_margin: float
    qty_by_cost: int
    qty_by_margin: int
    qty_by_portfolio: int
    final_qty: int


@dataclass(slots=True)
class ExecutionPlan:
    structure: StructureType
    direction: Direction
    legs: List[OptionQuote]
    qty: int
    max_risk_usd: float
    trigger_mode: TriggerMode
    trigger_price: Optional[float]
    invalidation_price: Optional[float]
    notes: List[str] = field(default_factory=list)


@dataclass(slots=True)
class PositionSnapshot:
    entry_time: datetime
    direction: Direction
    structure: StructureType
    entry_underlying_price: float
    entry_option_cost: float
    current_option_value: float
    current_underlying_price: float
    bars_in_trade: int
    dte_remaining: int
    realized_r_multiple: float = 0.0
    reduced_once: bool = False


@dataclass(slots=True)
class ExitDecision:
    should_exit: bool
    reason: ExitReason
    reduce_only: bool = False
    notes: List[str] = field(default_factory=list)
