from __future__ import annotations

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
