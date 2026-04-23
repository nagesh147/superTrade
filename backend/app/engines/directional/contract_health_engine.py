from __future__ import annotations

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
