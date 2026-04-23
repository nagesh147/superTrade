from __future__ import annotations

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
