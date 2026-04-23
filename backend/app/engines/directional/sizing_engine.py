from __future__ import annotations

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
