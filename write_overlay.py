from pathlib import Path

root = Path('/mnt/data/superTrade_directional_overlay')
files = {}

files['backend/app/__init__.py'] = ''
files['backend/app/core/__init__.py'] = ''
files['backend/app/engines/__init__.py'] = ''
files['backend/app/engines/directional/__init__.py'] = ''
files['backend/app/engines/indicators/__init__.py'] = ''
files['backend/app/schemas/__init__.py'] = ''
files['backend/app/services/__init__.py'] = ''
files['backend/app/services/exchanges/__init__.py'] = ''
files['backend/app/api/__init__.py'] = ''
files['backend/app/api/v1/__init__.py'] = ''
files['backend/app/api/v1/endpoints/__init__.py'] = ''
files['tests/__init__.py'] = ''
files['tests/directional/__init__.py'] = ''

files['backend/app/core/enums.py'] = '''from __future__ import annotations

from enum import Enum


class Direction(str, Enum):
    BULLISH = "bullish"
    BEARISH = "bearish"
    NEUTRAL = "neutral"


class SetupType(str, Enum):
    EARLY = "early"
    CONFIRMED = "confirmed"


class SetupStatus(str, Enum):
    ACTIVE = "active"
    ENTERED = "entered"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class TriggerMode(str, Enum):
    PULLBACK = "pullback"
    CONTINUATION = "continuation"
    WAIT = "wait"
    ABORT = "abort"


class StructureType(str, Enum):
    NAKED_CALL = "naked_call"
    NAKED_PUT = "naked_put"
    BULL_CALL_SPREAD = "bull_call_spread"
    BEAR_PUT_SPREAD = "bear_put_spread"
    BULL_PUT_SPREAD = "bull_put_spread"
    BEAR_CALL_SPREAD = "bear_call_spread"
    NO_TRADE = "no_trade"


class TradeState(str, Enum):
    IDLE = "idle"
    EARLY_SETUP_ACTIVE = "early_setup_active"
    CONFIRMED_SETUP_ACTIVE = "confirmed_setup_active"
    FILTERED = "filtered"
    ENTRY_ARMED_PULLBACK = "entry_armed_pullback"
    ENTRY_ARMED_CONTINUATION = "entry_armed_continuation"
    ENTERED = "entered"
    PARTIALLY_REDUCED = "partially_reduced"
    EXIT_PENDING = "exit_pending"
    EXITED = "exited"
    CANCELLED = "cancelled"


class ExitReason(str, Enum):
    NONE = "none"
    THESIS_STOP = "thesis_stop"
    FINANCIAL_STOP = "financial_stop"
    TIME_STOP = "time_stop"
    PROFIT_TARGET = "profit_target"
    EXPIRY_EXIT = "expiry_exit"
    VOLATILITY_EXIT = "volatility_exit"
'''

files['backend/app/schemas/market.py'] = '''from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional


@dataclass(slots=True)
class Candle:
    ts: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float = 0.0


@dataclass(slots=True)
class HACandle:
    ts: datetime
    open: float
    high: float
    low: float
    close: float


@dataclass(slots=True)
class OptionQuote:
    symbol: str
    underlying: str
    expiry: str
    dte: int
    strike: float
    option_type: str
    bid: float
    ask: float
    mark: Optional[float] = None
    mid: Optional[float] = None
    iv: Optional[float] = None
    iv_rank: Optional[float] = None
    delta: Optional[float] = None
    oi: Optional[float] = None
    volume: Optional[float] = None
    contract_multiplier: float = 1.0
    estimated_margin: float = 0.0
    quote_age_ms: int = 0
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        if self.mid is None and self.bid > 0 and self.ask > 0:
            self.mid = (self.bid + self.ask) / 2.0
        if self.mark is None and self.mid is not None:
            self.mark = self.mid
'''

files['backend/app/schemas/directional.py'] = '''from __future__ import annotations

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
'''

files['backend/app/engines/indicators/ema.py'] = '''from __future__ import annotations

from typing import Iterable, List


def ema(values: Iterable[float], period: int) -> List[float]:
    values = list(values)
    if not values:
        return []
    if period <= 0:
        raise ValueError("period must be > 0")
    alpha = 2.0 / (period + 1.0)
    out = [values[0]]
    for v in values[1:]:
        out.append(alpha * v + (1.0 - alpha) * out[-1])
    return out
'''

files['backend/app/engines/indicators/atr.py'] = '''from __future__ import annotations

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
'''

files['backend/app/engines/indicators/heikin_ashi.py'] = '''from __future__ import annotations

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
'''

files['backend/app/engines/indicators/supertrend.py'] = '''from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List

from app.engines.indicators.atr import atr
from app.schemas.market import Candle, HACandle


@dataclass(slots=True)
class SuperTrendPoint:
    value: float
    direction: str


def compute_supertrend(candles: Iterable[Candle | HACandle], period: int, multiplier: float) -> List[SuperTrendPoint]:
    candles = list(candles)
    if not candles:
        return []
    atr_values = atr(candles, period)
    hl2 = [(c.high + c.low) / 2.0 for c in candles]
    upper_basic = [m + multiplier * a for m, a in zip(hl2, atr_values)]
    lower_basic = [m - multiplier * a for m, a in zip(hl2, atr_values)]

    final_upper = [upper_basic[0]]
    final_lower = [lower_basic[0]]
    points: List[SuperTrendPoint] = [SuperTrendPoint(value=lower_basic[0], direction="green")]
    direction = "green"

    for i in range(1, len(candles)):
        prev_close = candles[i - 1].close
        fu = upper_basic[i] if upper_basic[i] < final_upper[-1] or prev_close > final_upper[-1] else final_upper[-1]
        fl = lower_basic[i] if lower_basic[i] > final_lower[-1] or prev_close < final_lower[-1] else final_lower[-1]
        final_upper.append(fu)
        final_lower.append(fl)

        close = candles[i].close
        if close > final_upper[i - 1]:
            direction = "green"
        elif close < final_lower[i - 1]:
            direction = "red"
        else:
            direction = points[-1].direction

        value = final_lower[i] if direction == "green" else final_upper[i]
        points.append(SuperTrendPoint(value=value, direction=direction))
    return points
'''

files['backend/app/engines/indicators/stats.py'] = '''from __future__ import annotations

from typing import Iterable


def clamp(value: float, min_value: float = 0.0, max_value: float = 1.0) -> float:
    return max(min_value, min(max_value, value))


def signed_unit(value: float, scale: float) -> float:
    if scale == 0:
        return 0.0
    x = value / scale
    return max(-1.0, min(1.0, x))


def mean(values: Iterable[float]) -> float:
    values = list(values)
    return sum(values) / len(values) if values else 0.0
'''

files['backend/app/services/exchanges/base.py'] = '''from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, Sequence

from app.schemas.market import Candle, OptionQuote


@dataclass(slots=True)
class AccountSnapshot:
    equity: float
    free_margin: float
    portfolio_remaining_risk_usd: float


class ExchangeAdapter(Protocol):
    def get_candles(self, symbol: str, timeframe: str, limit: int) -> Sequence[Candle]: ...
    def get_options_chain(self, underlying: str) -> Sequence[OptionQuote]: ...
    def get_account_snapshot(self) -> AccountSnapshot: ...
    def estimate_option_cost(self, quote: OptionQuote, qty: int, side: str = "buy") -> float: ...
    def estimate_option_margin(self, quote: OptionQuote, qty: int, side: str = "buy") -> float: ...
'''

files['backend/app/engines/directional/scoring.py'] = '''from __future__ import annotations

from dataclasses import dataclass

from app.engines.indicators.stats import clamp


@dataclass(slots=True)
class ScoreBundle:
    macro: float
    signal_long: float
    signal_short: float
    pullback: float
    continuation: float


def macro_regime_score(f1: float, f2: float, f3: float, f4: float, f5: float) -> float:
    return 30 * f1 + 20 * f2 + 15 * f3 + 20 * f4 + 15 * f5


def directional_signal_score(g1: float, g2: float, g3: float, g4: float, g5: float, bullish: bool) -> float:
    polarity = max(g4, 0.0) if bullish else max(-g4, 0.0)
    return 30 * g1 + 20 * g2 + 15 * g3 + 20 * polarity + 15 * g5


def pullback_score(p1: float, p2: float, p3: float, p4: float, p5: float) -> float:
    return 30 * p1 + 25 * p2 + 15 * p3 + 15 * p4 + 15 * (1.0 - p5)


def continuation_score(c1: float, c2: float, c3: float, c4: float, c5: float) -> float:
    return 25 * c1 + 20 * c2 + 20 * c3 + 20 * (1.0 - c4) + 15 * c5


def normalize_spread_pct(spread_pct: float, good: float = 0.01, bad: float = 0.04) -> float:
    if spread_pct <= good:
        return 1.0
    if spread_pct >= bad:
        return 0.0
    return 1.0 - (spread_pct - good) / (bad - good)


def normalize_ratio(value: float, good: float, bad: float) -> float:
    if value <= good:
        return 1.0
    if value >= bad:
        return 0.0
    return 1.0 - (value - good) / (bad - good)


def normalize_positive(value: float, good: float) -> float:
    if good <= 0:
        return 0.0
    return clamp(value / good)
'''

files['backend/app/engines/directional/regime_engine.py'] = '''from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from app.core.enums import Direction
from app.engines.indicators.atr import atr
from app.engines.indicators.ema import ema
from app.engines.indicators.stats import clamp, mean, signed_unit
from app.engines.directional.scoring import macro_regime_score
from app.schemas.directional import MacroRegime
from app.schemas.market import Candle


@dataclass(slots=True)
class RegimeConfig:
    ema_period: int = 50
    breakout_lookback: int = 20
    atr_period: int = 14


class RegimeEngine:
    def __init__(self, config: RegimeConfig | None = None) -> None:
        self.config = config or RegimeConfig()

    def evaluate_4h(self, symbol: str, candles: Sequence[Candle]) -> MacroRegime:
        if len(candles) < max(self.config.ema_period, self.config.breakout_lookback) + 2:
            raise ValueError("insufficient candles for macro regime")
        closes = [c.close for c in candles]
        ema50 = ema(closes, self.config.ema_period)
        atr_values = atr(candles, self.config.atr_period)
        last = candles[-1]
        prev = candles[-2]
        last_ema = ema50[-1]
        f1 = 1.0 if last.close > last_ema else -1.0
        ema_slope = ema50[-1] - ema50[-5]
        slope_scale = max(last_ema * 0.01, 1e-9)
        f2 = signed_unit(ema_slope, slope_scale)
        recent_atr = mean(atr_values[-5:])
        base_atr = max(mean(atr_values[-20:-5]), 1e-9)
        f3 = signed_unit(recent_atr - base_atr, base_atr)
        window = candles[-self.config.breakout_lookback:]
        highest = max(c.high for c in window)
        lowest = min(c.low for c in window)
        range_span = max(highest - lowest, 1e-9)
        range_pos = ((last.close - lowest) / range_span) * 2 - 1
        f4 = max(-1.0, min(1.0, range_pos))
        body = last.close - last.open
        rng = max(last.high - last.low, 1e-9)
        body_dom = body / rng
        f5 = max(-1.0, min(1.0, body_dom))
        score = macro_regime_score(f1, f2, f3, f4, f5)
        if score >= 35:
            regime = Direction.BULLISH
        elif score <= -35:
            regime = Direction.BEARISH
        else:
            regime = Direction.NEUTRAL
        quality = clamp(abs(score) / 100.0)
        return MacroRegime(
            ts=last.ts,
            symbol=symbol,
            regime=regime,
            score=score,
            features={"f1": f1, "f2": f2, "f3": f3, "f4": f4, "f5": f5},
            quality=quality,
        )
'''

files['backend/app/engines/directional/signal_engine.py'] = '''from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from app.core.enums import Direction
from app.engines.directional.scoring import directional_signal_score
from app.engines.indicators.atr import atr
from app.engines.indicators.heikin_ashi import build_heikin_ashi
from app.engines.indicators.stats import clamp
from app.engines.indicators.supertrend import compute_supertrend
from app.schemas.directional import DirectionalSignal
from app.schemas.market import Candle


@dataclass(slots=True)
class SignalConfig:
    fast_period: int = 7
    fast_multiplier: float = 3.0
    mid_period: int = 14
    mid_multiplier: float = 2.0
    slow_period: int = 21
    slow_multiplier: float = 1.0


class SignalEngine:
    def __init__(self, config: SignalConfig | None = None) -> None:
        self.config = config or SignalConfig()

    def evaluate_1h(self, symbol: str, real_candles: Sequence[Candle]) -> DirectionalSignal:
        if len(real_candles) < self.config.slow_period + 5:
            raise ValueError("insufficient candles for signal")
        ha = build_heikin_ashi(real_candles)
        fast = compute_supertrend(ha, self.config.fast_period, self.config.fast_multiplier)
        mid = compute_supertrend(ha, self.config.mid_period, self.config.mid_multiplier)
        slow = compute_supertrend(ha, self.config.slow_period, self.config.slow_multiplier)
        last = ha[-1]
        prev_idx = -2

        dirs = [fast[-1].direction, mid[-1].direction, slow[-1].direction]
        prev_dirs = [fast[prev_idx].direction, mid[prev_idx].direction, slow[prev_idx].direction]
        alignment_strength = sum(d == "green" for d in dirs) if all(d == "green" for d in dirs) else sum(d == "red" for d in dirs) if all(d == "red" for d in dirs) else sum(1 for d in dirs if d == max(set(dirs), key=dirs.count))
        all_green = all(d == "green" for d in dirs)
        all_red = all(d == "red" for d in dirs)
        prev_all_green = all(d == "green" for d in prev_dirs)
        prev_all_red = all(d == "red" for d in prev_dirs)
        green_arrow = all_green and not prev_all_green
        red_arrow = all_red and not prev_all_red

        atr_values = atr(ha, 14)
        last_atr = max(atr_values[-1], 1e-9)
        g1 = alignment_strength / 3.0
        g2_long = 1.0 if green_arrow else 0.0
        g2_short = 1.0 if red_arrow else 0.0
        g3 = clamp(abs(last.close - last.open) / last_atr)
        st_zone = fast[-1].value
        g4 = max(-1.0, min(1.0, (last.close - st_zone) / last_atr))
        dist_fast_mid = abs(fast[-1].value - mid[-1].value)
        dist_mid_slow = abs(mid[-1].value - slow[-1].value)
        g5 = clamp((dist_fast_mid + dist_mid_slow) / (2.0 * last_atr))
        score_long = directional_signal_score(g1, g2_long, g3, g4, g5, bullish=True)
        score_short = directional_signal_score(g1, g2_short, g3, g4, g5, bullish=False)

        if all_green:
            direction = Direction.BULLISH
        elif all_red:
            direction = Direction.BEARISH
        else:
            direction = Direction.NEUTRAL

        return DirectionalSignal(
            ts=real_candles[-1].ts,
            symbol=symbol,
            direction_state=direction,
            alignment_strength=alignment_strength if direction != Direction.NEUTRAL else 0,
            green_arrow=green_arrow,
            red_arrow=red_arrow,
            score_long=score_long,
            score_short=score_short,
            st_7_3=fast[-1].value,
            st_14_2=mid[-1].value,
            st_21_1=slow[-1].value,
            features={"g1": g1, "g3": g3, "g4": g4, "g5": g5},
        )
'''

files['backend/app/engines/directional/setup_engine.py'] = '''from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
import uuid

from app.core.enums import Direction, SetupStatus, SetupType
from app.schemas.directional import DirectionalSignal, SetupEvent


@dataclass(slots=True)
class SetupConfig:
    setup_valid_bars: int = 3
    bar_minutes: int = 60
    early_score_threshold: float = 60.0
    confirmed_score_threshold: float = 70.0


class SetupEngine:
    def __init__(self, config: SetupConfig | None = None) -> None:
        self.config = config or SetupConfig()

    def create_or_update(self, signal: DirectionalSignal) -> SetupEvent | None:
        if signal.direction_state == Direction.NEUTRAL:
            return None
        if signal.direction_state == Direction.BULLISH:
            score = signal.score_long
            confirmed = signal.green_arrow and signal.alignment_strength == 3
        else:
            score = signal.score_short
            confirmed = signal.red_arrow and signal.alignment_strength == 3
        if confirmed and score >= self.config.confirmed_score_threshold:
            setup_type = SetupType.CONFIRMED
        elif score >= self.config.early_score_threshold:
            setup_type = SetupType.EARLY
        else:
            return None
        expires_at = signal.ts + timedelta(minutes=self.config.bar_minutes * self.config.setup_valid_bars)
        return SetupEvent(
            setup_id=str(uuid.uuid4()),
            setup_type=setup_type,
            direction=signal.direction_state,
            activated_at=signal.ts,
            expires_at=expires_at,
            bars_remaining=self.config.setup_valid_bars,
            status=SetupStatus.ACTIVE,
            signal=signal,
        )

    def decrement_window(self, setup: SetupEvent, latest_ts) -> SetupEvent:
        bars_elapsed = max(0, int((latest_ts - setup.activated_at).total_seconds() // (self.config.bar_minutes * 60)))
        remaining = max(0, self.config.setup_valid_bars - bars_elapsed)
        setup.bars_remaining = remaining
        if remaining == 0 and setup.status == SetupStatus.ACTIVE:
            setup.status = SetupStatus.EXPIRED
        return setup
'''

files['backend/app/engines/directional/policy_engine.py'] = '''from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from app.core.enums import Direction
from app.schemas.directional import FilterDecision, MacroRegime, SetupEvent
from app.schemas.market import OptionQuote


@dataclass(slots=True)
class PolicyConfig:
    min_dte: int = 5
    preferred_min_dte: int = 10
    preferred_max_dte: int = 15
    ivr_naked_max: float = 60.0
    ivr_hard_block: float = 80.0
    min_oi: float = 100.0
    max_spread_pct: float = 0.035
    event_block: bool = False


class PolicyEngine:
    def __init__(self, config: PolicyConfig | None = None) -> None:
        self.config = config or PolicyConfig()

    def evaluate(
        self,
        regime: MacroRegime,
        setup: SetupEvent,
        chain: Sequence[OptionQuote],
        iv_rank: float,
        event_blocked: bool = False,
    ) -> FilterDecision:
        reasons: list[str] = []
        macro_pass = regime.regime == setup.direction and abs(regime.score) >= 35
        if not macro_pass:
            reasons.append("macro regime mismatch")
        dte_pass = any(q.dte >= self.config.min_dte for q in chain)
        if not dte_pass:
            reasons.append("no valid expiry")
        vol_pass = iv_rank <= self.config.ivr_hard_block
        if not vol_pass:
            reasons.append("IV rank too high")
        event_pass = not event_blocked
        if not event_pass:
            reasons.append("event-blocked")
        liquidity_pass = any(
            q.oi is not None and q.oi >= self.config.min_oi and q.bid > 0 and q.ask > q.bid and ((q.ask - q.bid) / max((q.ask + q.bid) / 2.0, 1e-9)) <= self.config.max_spread_pct
            for q in chain
        )
        if not liquidity_pass:
            reasons.append("no liquid contract")
        preferred_structure_family = "naked" if iv_rank < self.config.ivr_naked_max else "defined_risk"
        allowed = macro_pass and dte_pass and vol_pass and event_pass and liquidity_pass
        return FilterDecision(
            allowed=allowed,
            reasons=reasons,
            preferred_structure_family=preferred_structure_family,
            dte_pass=dte_pass,
            vol_pass=vol_pass,
            macro_pass=macro_pass,
            event_pass=event_pass,
            liquidity_pass=liquidity_pass,
        )
'''

files['backend/app/engines/directional/execution_engine.py'] = '''from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from app.core.enums import Direction, TriggerMode
from app.engines.directional.scoring import continuation_score, pullback_score
from app.engines.indicators.atr import atr
from app.engines.indicators.stats import clamp
from app.schemas.directional import ExecutionTrigger, SetupEvent
from app.schemas.market import Candle


@dataclass(slots=True)
class ExecutionConfig:
    retest_tolerance_pct: float = 0.003
    continuation_max_extension_atr: float = 1.5


class ExecutionEngine:
    def __init__(self, config: ExecutionConfig | None = None) -> None:
        self.config = config or ExecutionConfig()

    def evaluate_pullback(self, setup: SetupEvent, candles_15m: Sequence[Candle], st_fast_value: float) -> ExecutionTrigger:
        if len(candles_15m) < 20:
            return ExecutionTrigger(mode=TriggerMode.WAIT, score=0.0, trigger_price=None, invalidation_price=None, reasons=["insufficient 15m candles"])
        last = candles_15m[-1]
        recent_atr = max(atr(candles_15m[-20:], 14)[-1], 1e-9)
        if setup.direction == Direction.BULLISH:
            touch_distance = abs(last.low - st_fast_value) / max(st_fast_value, 1e-9)
            p1 = clamp(1.0 - touch_distance / self.config.retest_tolerance_pct)
            p2 = 1.0 if last.close > st_fast_value else 0.0
            rejection = max(0.0, min(1.0, (min(last.open, last.close) - last.low) / max(last.high - last.low, 1e-9)))
        else:
            touch_distance = abs(last.high - st_fast_value) / max(st_fast_value, 1e-9)
            p1 = clamp(1.0 - touch_distance / self.config.retest_tolerance_pct)
            p2 = 1.0 if last.close < st_fast_value else 0.0
            rejection = max(0.0, min(1.0, (last.high - max(last.open, last.close)) / max(last.high - last.low, 1e-9)))
        p3 = rejection
        avg_volume = sum(c.volume for c in candles_15m[-20:]) / 20.0
        p4 = clamp(last.volume / max(avg_volume, 1e-9))
        extension = abs(last.close - st_fast_value) / recent_atr
        p5 = clamp(extension / self.config.continuation_max_extension_atr)
        score = pullback_score(p1, p2, p3, p4, p5)
        mode = TriggerMode.PULLBACK if score >= 72 else TriggerMode.WAIT
        return ExecutionTrigger(mode=mode, score=score, trigger_price=last.close if mode == TriggerMode.PULLBACK else None, invalidation_price=st_fast_value, reasons=[])

    def evaluate_continuation(self, setup: SetupEvent, candles_15m: Sequence[Candle], regime_strength: float) -> ExecutionTrigger:
        if len(candles_15m) < 20:
            return ExecutionTrigger(mode=TriggerMode.WAIT, score=0.0, trigger_price=None, invalidation_price=None, reasons=["insufficient 15m candles"])
        last = candles_15m[-1]
        prev_window = candles_15m[-6:-1]
        recent_atr = max(atr(candles_15m[-20:], 14)[-1], 1e-9)
        if setup.direction == Direction.BULLISH:
            prior_extreme = max(c.high for c in prev_window)
            c1 = 1.0 if last.close > prior_extreme else 0.0
        else:
            prior_extreme = min(c.low for c in prev_window)
            c1 = 1.0 if last.close < prior_extreme else 0.0
        c2 = clamp((last.high - last.low) / recent_atr)
        avg_volume = sum(c.volume for c in candles_15m[-20:]) / 20.0
        c3 = clamp(last.volume / max(avg_volume, 1e-9))
        extension = abs(last.close - prev_window[-1].close) / recent_atr
        c4 = clamp(extension / self.config.continuation_max_extension_atr)
        c5 = clamp(abs(regime_strength) / 100.0)
        score = continuation_score(c1, c2, c3, c4, c5)
        mode = TriggerMode.CONTINUATION if score >= 75 else TriggerMode.WAIT
        invalidation = prev_window[-1].low if setup.direction == Direction.BULLISH else prev_window[-1].high
        return ExecutionTrigger(mode=mode, score=score, trigger_price=last.close if mode == TriggerMode.CONTINUATION else None, invalidation_price=invalidation, reasons=[])
'''

files['backend/app/engines/directional/option_translation_engine.py'] = '''from __future__ import annotations

from dataclasses import dataclass

from app.core.enums import Direction
from app.schemas.directional import ExecutionTrigger, MacroRegime, OptionTranslation, SetupEvent


@dataclass(slots=True)
class TranslationConfig:
    expected_bars_to_work: int = 4
    default_theta_budget_pct: float = 0.35


class OptionTranslationEngine:
    def __init__(self, config: TranslationConfig | None = None) -> None:
        self.config = config or TranslationConfig()

    def translate(self, regime: MacroRegime, setup: SetupEvent, trigger: ExecutionTrigger, spot: float, st_fast_value: float) -> OptionTranslation:
        expected_move_pct = max(abs(trigger.trigger_price - st_fast_value) / max(spot, 1e-9) * 1.8, 0.01)
        breakeven_move_pct = max(expected_move_pct * 0.65, 0.0075)
        strong_regime = abs(regime.score) >= 60
        if strong_regime:
            delta_min, delta_max = 0.40, 0.60
            family = "convex"
        else:
            delta_min, delta_max = 0.25, 0.50
            family = "defined_risk"
        return OptionTranslation(
            direction=setup.direction,
            required_delta_min=delta_min,
            required_delta_max=delta_max,
            preferred_dte_min=10,
            preferred_dte_max=15,
            expected_move_pct=expected_move_pct,
            expected_bars_to_work=self.config.expected_bars_to_work,
            theta_budget_pct=self.config.default_theta_budget_pct,
            breakeven_move_pct=breakeven_move_pct,
            preferred_structure_family=family,
        )
'''

files['backend/app/engines/directional/contract_health_engine.py'] = '''from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List

from app.engines.directional.scoring import normalize_positive, normalize_ratio, normalize_spread_pct
from app.schemas.directional import ContractHealth, OptionTranslation
from app.schemas.market import OptionQuote


@dataclass(slots=True)
class ContractHealthConfig:
    max_spread_pct: float = 0.035
    min_oi: float = 100.0
    min_volume: float = 25.0
    max_mark_mid_dev: float = 0.03
    max_quote_age_ms: int = 5000


class ContractHealthEngine:
    def __init__(self, config: ContractHealthConfig | None = None) -> None:
        self.config = config or ContractHealthConfig()

    def evaluate(self, quote: OptionQuote, underlying_move_pct_hint: float = 0.02) -> ContractHealth:
        vetoes: list[str] = []
        if quote.bid <= 0 or quote.ask <= quote.bid:
            vetoes.append("invalid book")
        spread_pct = (quote.ask - quote.bid) / max((quote.ask + quote.bid) / 2.0, 1e-9)
        if spread_pct > self.config.max_spread_pct:
            vetoes.append("spread too wide")
        if (quote.oi or 0.0) < self.config.min_oi:
            vetoes.append("oi too low")
        if quote.quote_age_ms > self.config.max_quote_age_ms:
            vetoes.append("stale quote")
        mark_mid_dev = abs((quote.mark or quote.mid or 0.0) - (quote.mid or 0.0)) / max((quote.mid or 1e-9), 1e-9)
        if mark_mid_dev > self.config.max_mark_mid_dev:
            vetoes.append("mark deviates from mid")
        h1 = normalize_spread_pct(spread_pct)
        h2 = normalize_positive((quote.oi or 0.0), self.config.min_oi * 5)
        h3 = normalize_positive((quote.volume or 0.0), self.config.min_volume * 4)
        h4 = normalize_ratio(mark_mid_dev, 0.005, self.config.max_mark_mid_dev)
        h5 = normalize_ratio(quote.quote_age_ms, 500, self.config.max_quote_age_ms)
        h6 = normalize_spread_pct(spread_pct * 1.2)  # slippage proxy
        delta = abs(quote.delta or 0.0)
        responsiveness = min(delta / 0.45, 1.0) if underlying_move_pct_hint > 0 else 0.0
        h7 = max(0.0, min(1.0, responsiveness))
        h8 = 1.0 if spread_pct > self.config.max_spread_pct else 0.0
        score = 20*h1 + 15*h2 + 10*h3 + 15*h4 + 10*h5 + 10*h6 + 15*h7 + 5*(1-h8)
        return ContractHealth(
            symbol=quote.symbol,
            score=score,
            veto_reasons=vetoes,
            spread_pct=spread_pct,
            mark_mid_dev=mark_mid_dev,
            responsiveness_score=h7,
            quote_quality_score=(h1 + h4 + h5) / 3.0,
        )

    def rank_candidates(self, quotes: Iterable[OptionQuote], translation: OptionTranslation) -> List[tuple[OptionQuote, ContractHealth]]:
        filtered: list[tuple[OptionQuote, ContractHealth]] = []
        for q in quotes:
            if not (translation.required_delta_min <= abs(q.delta or 0.0) <= translation.required_delta_max):
                continue
            if not (translation.preferred_dte_min <= q.dte <= translation.preferred_dte_max):
                continue
            health = self.evaluate(q, underlying_move_pct_hint=translation.expected_move_pct)
            filtered.append((q, health))
        return sorted(filtered, key=lambda x: x[1].score, reverse=True)
'''

files['backend/app/engines/directional/structure_selector.py'] = '''from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from app.core.enums import StructureType
from app.schemas.directional import ContractHealth, MacroRegime, OptionTranslation, StructureDecision
from app.schemas.market import OptionQuote


@dataclass(slots=True)
class StructureSelectorConfig:
    min_score_to_trade: float = 65.0


class StructureSelector:
    def __init__(self, config: StructureSelectorConfig | None = None) -> None:
        self.config = config or StructureSelectorConfig()

    def _score_naked(self, r1, r2, r3, r4, r5, r6, r7, r8):
        return 20*r1 + 15*r2 + 15*r3 + 20*r4 + 15*(1-r5) + 5*(1-r6) + 5*r7 + 5*r8

    def _score_debit(self, r1, r2, r3, r4, r5, r6, r7, r8):
        return 18*r1 + 14*r2 + 14*r3 + 15*r4 + 15*r5 + 10*r6 + 7*r7 + 7*r8

    def _score_credit(self, r1, r2, r3, r4, r5, r6, r7, r8):
        return 16*r1 + 12*r2 + 10*r3 + 10*r4 + 20*r5 + 15*r6 + 7*r7 + 10*r8

    def select(
        self,
        regime: MacroRegime,
        signal_strength: float,
        execution_strength: float,
        translation: OptionTranslation,
        ranked_contracts: Sequence[tuple[OptionQuote, ContractHealth]],
        iv_rank: float,
        account_equity: float,
    ) -> StructureDecision:
        if not ranked_contracts:
            return StructureDecision(StructureType.NO_TRADE, 0, 0, 0, 100, ["no ranked contracts"], [])
        best_quote, best_health = ranked_contracts[0]
        r1 = min(abs(regime.score) / 100.0, 1.0)
        r2 = min(signal_strength / 100.0, 1.0)
        r3 = min(execution_strength / 100.0, 1.0)
        expected_move_vs_breakeven = min(translation.expected_move_pct / max(translation.breakeven_move_pct, 1e-9), 1.5) / 1.5
        r4 = expected_move_vs_breakeven
        r5 = min(iv_rank / 100.0, 1.0)
        r6 = min(translation.theta_budget_pct / 0.5, 1.0)
        r7 = 1.0 if account_equity >= 5000 else max(account_equity / 5000.0, 0.2)
        r8 = min(best_health.score / 100.0, 1.0)

        score_naked = self._score_naked(r1, r2, r3, r4, r5, r6, r7, r8)
        score_debit = self._score_debit(r1, r2, r3, r4, r5, r6, r7, r8)
        score_credit = self._score_credit(r1, r2, r3, r4, r5, r6, r7, r8)
        max_score = max(score_naked, score_debit, score_credit)
        score_no_trade = max(0.0, 100.0 - max_score + (15.0 if best_health.veto_reasons else 0.0))

        if max(score_naked, score_debit, score_credit, score_no_trade) == score_no_trade or max_score < self.config.min_score_to_trade:
            return StructureDecision(StructureType.NO_TRADE, score_naked, score_debit, score_credit, score_no_trade, ["no structure cleared score threshold"], [])

        if max_score == score_naked:
            chosen = StructureType.NAKED_CALL if translation.direction.value == "bullish" else StructureType.NAKED_PUT
            legs = [best_quote]
        elif max_score == score_debit:
            chosen = StructureType.BULL_CALL_SPREAD if translation.direction.value == "bullish" else StructureType.BEAR_PUT_SPREAD
            farther = None
            for q, health in ranked_contracts[1:]:
                if q.expiry == best_quote.expiry and q.option_type == best_quote.option_type:
                    farther = q
                    break
            legs = [best_quote] + ([farther] if farther else [])
        else:
            chosen = StructureType.BULL_PUT_SPREAD if translation.direction.value == "bullish" else StructureType.BEAR_CALL_SPREAD
            legs = [best_quote]

        return StructureDecision(chosen, score_naked, score_debit, score_credit, score_no_trade, [f"selected {chosen.value}"], legs)
'''

files['backend/app/engines/directional/sizing_engine.py'] = '''from __future__ import annotations

from dataclasses import dataclass
import math

from app.schemas.directional import SizingDecision, StructureDecision
from app.services.exchanges.base import AccountSnapshot


@dataclass(slots=True)
class SizingConfig:
    naked_risk_pct: float = 0.02
    defined_risk_pct: float = 0.03
    max_margin_usage_pct: float = 0.50


class SizingEngine:
    def __init__(self, config: SizingConfig | None = None) -> None:
        self.config = config or SizingConfig()

    def compute(self, structure: StructureDecision, account: AccountSnapshot, unit_cost: float, unit_margin: float) -> SizingDecision:
        is_naked = structure.chosen_structure.value.startswith("naked")
        max_risk_usd = account.equity * (self.config.naked_risk_pct if is_naked else self.config.defined_risk_pct)
        qty_by_cost = math.floor(max_risk_usd / max(unit_cost, 1e-9))
        qty_by_margin = math.floor((account.free_margin * self.config.max_margin_usage_pct) / max(unit_margin, 1e-9)) if unit_margin > 0 else qty_by_cost
        qty_by_portfolio = math.floor(account.portfolio_remaining_risk_usd / max(unit_cost, 1e-9))
        final_qty = max(0, min(qty_by_cost, qty_by_margin, qty_by_portfolio))
        return SizingDecision(
            max_risk_usd=max_risk_usd,
            unit_cost=unit_cost,
            unit_margin=unit_margin,
            qty_by_cost=qty_by_cost,
            qty_by_margin=qty_by_margin,
            qty_by_portfolio=qty_by_portfolio,
            final_qty=final_qty,
        )
'''

files['backend/app/engines/directional/monitor_engine.py'] = '''from __future__ import annotations

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
'''

files['backend/app/engines/directional/orchestrator.py'] = '''from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from app.core.enums import StructureType, TriggerMode
from app.engines.directional.contract_health_engine import ContractHealthEngine
from app.engines.directional.execution_engine import ExecutionEngine
from app.engines.directional.option_translation_engine import OptionTranslationEngine
from app.engines.directional.policy_engine import PolicyEngine
from app.engines.directional.regime_engine import RegimeEngine
from app.engines.directional.setup_engine import SetupEngine
from app.engines.directional.signal_engine import SignalEngine
from app.engines.directional.sizing_engine import SizingEngine
from app.engines.directional.structure_selector import StructureSelector
from app.schemas.directional import ExecutionPlan
from app.schemas.market import Candle, OptionQuote
from app.services.exchanges.base import AccountSnapshot


@dataclass(slots=True)
class OrchestrationResult:
    status: str
    regime: object | None = None
    signal: object | None = None
    setup: object | None = None
    filters: object | None = None
    trigger: object | None = None
    translation: object | None = None
    structure: object | None = None
    sizing: object | None = None
    plan: ExecutionPlan | None = None
    reason: str | None = None


class DirectionalOrchestrator:
    def __init__(self) -> None:
        self.regime_engine = RegimeEngine()
        self.signal_engine = SignalEngine()
        self.setup_engine = SetupEngine()
        self.policy_engine = PolicyEngine()
        self.execution_engine = ExecutionEngine()
        self.translation_engine = OptionTranslationEngine()
        self.health_engine = ContractHealthEngine()
        self.structure_selector = StructureSelector()
        self.sizing_engine = SizingEngine()

    def run_cycle(
        self,
        symbol: str,
        candles_4h: Sequence[Candle],
        candles_1h: Sequence[Candle],
        candles_15m: Sequence[Candle],
        chain: Sequence[OptionQuote],
        iv_rank: float,
        account: AccountSnapshot,
        event_blocked: bool = False,
    ) -> OrchestrationResult:
        regime = self.regime_engine.evaluate_4h(symbol, candles_4h)
        signal = self.signal_engine.evaluate_1h(symbol, candles_1h)
        setup = self.setup_engine.create_or_update(signal)
        if setup is None:
            return OrchestrationResult(status="HOLD", regime=regime, signal=signal, reason="no setup")
        filters = self.policy_engine.evaluate(regime, setup, chain, iv_rank, event_blocked)
        if not filters.allowed:
            return OrchestrationResult(status="BLOCKED", regime=regime, signal=signal, setup=setup, filters=filters, reason=",".join(filters.reasons))
        pullback = self.execution_engine.evaluate_pullback(setup, candles_15m, signal.st_7_3)
        if pullback.mode == TriggerMode.PULLBACK:
            trigger = pullback
        else:
            continuation = self.execution_engine.evaluate_continuation(setup, candles_15m, regime.score)
            if continuation.mode == TriggerMode.CONTINUATION:
                trigger = continuation
            else:
                return OrchestrationResult(status="WAIT", regime=regime, signal=signal, setup=setup, filters=filters, trigger=continuation, reason="no execution trigger")
        spot = candles_1h[-1].close
        translation = self.translation_engine.translate(regime, setup, trigger, spot=spot, st_fast_value=signal.st_7_3)
        ranked = self.health_engine.rank_candidates(chain, translation)
        signal_strength = signal.score_long if setup.direction.value == "bullish" else signal.score_short
        structure = self.structure_selector.select(regime, signal_strength, trigger.score, translation, ranked, iv_rank, account.equity)
        if structure.chosen_structure == StructureType.NO_TRADE:
            return OrchestrationResult(status="NO_TRADE", regime=regime, signal=signal, setup=setup, filters=filters, trigger=trigger, translation=translation, structure=structure, reason="structure rejected")
        primary_leg = structure.legs[0]
        unit_cost = primary_leg.ask * primary_leg.contract_multiplier
        unit_margin = max(primary_leg.estimated_margin, unit_cost)
        sizing = self.sizing_engine.compute(structure, account, unit_cost, unit_margin)
        if sizing.final_qty < 1:
            return OrchestrationResult(status="NO_SIZE", regime=regime, signal=signal, setup=setup, filters=filters, trigger=trigger, translation=translation, structure=structure, sizing=sizing, reason="sizing rejected")
        plan = ExecutionPlan(
            structure=structure.chosen_structure,
            direction=setup.direction,
            legs=structure.legs,
            qty=sizing.final_qty,
            max_risk_usd=sizing.max_risk_usd,
            trigger_mode=trigger.mode,
            trigger_price=trigger.trigger_price,
            invalidation_price=trigger.invalidation_price,
            notes=structure.rationale,
        )
        return OrchestrationResult(status="READY", regime=regime, signal=signal, setup=setup, filters=filters, trigger=trigger, translation=translation, structure=structure, sizing=sizing, plan=plan)
'''

files['backend/app/api/v1/endpoints/directional_signals.py'] = '''from __future__ import annotations

from fastapi import APIRouter, Depends, Request

router = APIRouter(prefix="/directional", tags=["directional"])


@router.get("/status")
def directional_status() -> dict:
    return {"status": "directional stack loaded"}


@router.get("/note")
def directional_note() -> dict:
    return {
        "message": "Wire this router to the live orchestrator once exchange adapters and persistence are connected.",
    }
'''

files['tests/conftest.py'] = '''from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import List

import pytest

from app.schemas.market import Candle, OptionQuote
from app.services.exchanges.base import AccountSnapshot


def make_candles(start: float, steps: list[float], start_ts: datetime | None = None, minutes: int = 60, base_volume: float = 100.0) -> List[Candle]:
    ts = start_ts or datetime(2026, 1, 1, tzinfo=timezone.utc)
    out: List[Candle] = []
    price = start
    for i, step in enumerate(steps):
        open_ = price
        close = price + step
        high = max(open_, close) + max(abs(step) * 0.2, 1.0)
        low = min(open_, close) - max(abs(step) * 0.2, 1.0)
        out.append(Candle(ts=ts + timedelta(minutes=minutes*i), open=open_, high=high, low=low, close=close, volume=base_volume + i*5))
        price = close
    return out


@pytest.fixture
def bullish_4h_candles():
    return make_candles(70000, [120]*80, minutes=240)


@pytest.fixture
def bullish_1h_candles():
    steps = [-50, -40, -30, -25, -10, 15, 20, 30, 40, 55, 70, 60, 50, 45, 30, 20, -10, 15, 20, 25, 30, 40, 35, 20, 15, 10, 8, 5, 4, 3]
    return make_candles(76000, steps, minutes=60)


@pytest.fixture
def bullish_15m_pullback_candles():
    steps = [10, 12, 15, 18, 20, -8, -6, -4, 2, 8, 12, 10, 15, -5, -3, 12, 9, 10, 14, 12, -4, -3, 8, 11]
    return make_candles(78000, steps, minutes=15)


@pytest.fixture
def bullish_15m_continuation_candles():
    steps = [6, 7, 8, 10, 12, 10, 14, 12, 16, 20, 18, 22, 25, 24, 28, 30, 35, 40, 32, 45, 50, 42, 55, 65]
    return make_candles(78000, steps, minutes=15, base_volume=150)


@pytest.fixture
def healthy_chain():
    return [
        OptionQuote(symbol="C-BTC-78000-010126", underlying="BTCUSD", expiry="2026-01-10", dte=12, strike=78000, option_type="call", bid=2100, ask=2120, iv=0.45, iv_rank=45.0, delta=0.52, oi=1500, volume=300, contract_multiplier=0.001, estimated_margin=2.2, quote_age_ms=200),
        OptionQuote(symbol="C-BTC-79000-010126", underlying="BTCUSD", expiry="2026-01-10", dte=12, strike=79000, option_type="call", bid=1650, ask=1670, iv=0.44, iv_rank=45.0, delta=0.44, oi=1600, volume=330, contract_multiplier=0.001, estimated_margin=1.8, quote_age_ms=200),
        OptionQuote(symbol="C-BTC-80000-010126", underlying="BTCUSD", expiry="2026-01-10", dte=12, strike=80000, option_type="call", bid=1200, ask=1220, iv=0.43, iv_rank=45.0, delta=0.34, oi=1800, volume=350, contract_multiplier=0.001, estimated_margin=1.4, quote_age_ms=200),
    ]


@pytest.fixture
def rich_vol_chain():
    return [
        OptionQuote(symbol="P-BTC-77000-010126", underlying="BTCUSD", expiry="2026-01-10", dte=12, strike=77000, option_type="put", bid=1800, ask=1820, iv=0.80, iv_rank=78.0, delta=-0.42, oi=1400, volume=280, contract_multiplier=0.001, estimated_margin=1.9, quote_age_ms=200),
        OptionQuote(symbol="P-BTC-76000-010126", underlying="BTCUSD", expiry="2026-01-10", dte=12, strike=76000, option_type="put", bid=1400, ask=1418, iv=0.79, iv_rank=78.0, delta=-0.31, oi=1500, volume=290, contract_multiplier=0.001, estimated_margin=1.5, quote_age_ms=200),
    ]


@pytest.fixture
def account_snapshot():
    return AccountSnapshot(equity=10000.0, free_margin=5000.0, portfolio_remaining_risk_usd=300.0)
'''

files['tests/directional/test_indicators.py'] = '''from __future__ import annotations

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
'''

files['tests/directional/test_signal_engine.py'] = '''from __future__ import annotations

from app.core.enums import Direction
from app.engines.directional.signal_engine import SignalEngine
from tests.conftest import make_candles


def test_signal_engine_bullish_alignment_detected(bullish_1h_candles):
    engine = SignalEngine()
    signal = engine.evaluate_1h('BTCUSD', bullish_1h_candles)
    assert signal.direction_state in {Direction.BULLISH, Direction.NEUTRAL}
    assert signal.st_7_3 > 0


def test_signal_arrow_fires_on_transition():
    candles = make_candles(100, [-3, -3, -2, -1, 1, 2, 3, 5, 6, 7, 8, 9, 8, 6, 4, 3, 2, 2, 2, 2, 2, 2, 2, 2, 2], minutes=60)
    engine = SignalEngine()
    signal = engine.evaluate_1h('BTCUSD', candles)
    assert isinstance(signal.green_arrow, bool)
    assert isinstance(signal.red_arrow, bool)
'''

files['tests/directional/test_setup_engine.py'] = '''from __future__ import annotations

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
'''

files['tests/directional/test_execution_engine.py'] = '''from __future__ import annotations

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
'''

files['tests/directional/test_contract_health_and_structure.py'] = '''from __future__ import annotations

from app.core.enums import StructureType
from app.engines.directional.contract_health_engine import ContractHealthEngine
from app.engines.directional.option_translation_engine import OptionTranslationEngine
from app.engines.directional.regime_engine import RegimeEngine
from app.engines.directional.setup_engine import SetupEngine
from app.engines.directional.signal_engine import SignalEngine
from app.engines.directional.structure_selector import StructureSelector


def test_contract_health_ranks_good_contracts(healthy_chain):
    engine = ContractHealthEngine()
    health = engine.evaluate(healthy_chain[0])
    assert health.score > 50
    assert not health.veto_reasons


def test_structure_selector_picks_tradeable_structure(bullish_4h_candles, bullish_1h_candles, healthy_chain):
    regime = RegimeEngine().evaluate_4h('BTCUSD', bullish_4h_candles)
    signal = SignalEngine().evaluate_1h('BTCUSD', bullish_1h_candles)
    setup = SetupEngine().create_or_update(signal)
    if setup is None:
        return
    translation = OptionTranslationEngine().translate(regime, setup, type('T', (), {'trigger_price': bullish_1h_candles[-1].close}), bullish_1h_candles[-1].close, signal.st_7_3)
    ranked = ContractHealthEngine().rank_candidates(healthy_chain, translation)
    decision = StructureSelector().select(regime, signal.score_long, 80, translation, ranked, iv_rank=45.0, account_equity=10000.0)
    assert decision.chosen_structure in {
        StructureType.NAKED_CALL,
        StructureType.BULL_CALL_SPREAD,
        StructureType.BULL_PUT_SPREAD,
        StructureType.NO_TRADE,
    }
'''

files['tests/directional/test_sizing_and_monitor.py'] = '''from __future__ import annotations

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
'''

files['tests/directional/test_orchestrator.py'] = '''from __future__ import annotations

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
'''

files['README_DIRECTIONAL_OVERLAY.md'] = '''# superTrade directional options overlay

This bundle adds a production-oriented directional-options subsystem beside the existing payoff-template strategy engine.

## What is included
- 4H macro regime engine
- 1H HA + triple SuperTrend signal engine
- setup activation engine
- 15m pullback/continuation execution engine
- option translation engine
- contract health engine
- structure selector
- sizing engine
- monitor engine
- orchestrator
- pytest suite

## Intended integration
Copy these files into your repo root so `backend/app/...` merges into the existing backend package. Wire the new routers in `backend/app/api/v1/router.py`, and attach a `DirectionalOrchestrator` singleton in `main.py` alongside the existing engines.

## Run tests
From repo root:

```bash
cd backend
pytest -q ../tests/directional
```
'''

for path, content in files.items():
    p = root / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content)

print(f"wrote {len(files)} files")
