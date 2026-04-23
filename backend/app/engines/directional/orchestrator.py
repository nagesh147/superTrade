from __future__ import annotations

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
