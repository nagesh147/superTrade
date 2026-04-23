from __future__ import annotations

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
