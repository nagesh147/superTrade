from __future__ import annotations

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
