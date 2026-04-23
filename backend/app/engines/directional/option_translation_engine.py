from __future__ import annotations

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
