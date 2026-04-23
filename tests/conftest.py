from __future__ import annotations

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
