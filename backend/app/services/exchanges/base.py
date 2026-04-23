from __future__ import annotations

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
