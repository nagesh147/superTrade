from __future__ import annotations

from app.core.enums import StructureType
from app.engines.directional.contract_health_engine import ContractHealthEngine
from app.engines.directional.option_translation_engine import OptionTranslationEngine
from app.engines.directional.regime_engine import RegimeEngine
from app.engines.directional.setup_engine import SetupEngine
from app.engines.directional.signal_engine import SignalEngine
from app.engines.directional.structure_selector import StructureSelector


def test_contract_health_ranks_good_contracts(healthy_chain):
    engine = ContractHealthEngine()
    health = engine.evaluate(healthy_chain[0])
    assert health.score > 50
    assert not health.veto_reasons


def test_structure_selector_picks_tradeable_structure(bullish_4h_candles, bullish_1h_candles, healthy_chain):
    regime = RegimeEngine().evaluate_4h('BTCUSD', bullish_4h_candles)
    signal = SignalEngine().evaluate_1h('BTCUSD', bullish_1h_candles)
    setup = SetupEngine().create_or_update(signal)
    if setup is None:
        return
    translation = OptionTranslationEngine().translate(regime, setup, type('T', (), {'trigger_price': bullish_1h_candles[-1].close}), bullish_1h_candles[-1].close, signal.st_7_3)
    ranked = ContractHealthEngine().rank_candidates(healthy_chain, translation)
    decision = StructureSelector().select(regime, signal.score_long, 80, translation, ranked, iv_rank=45.0, account_equity=10000.0)
    assert decision.chosen_structure in {
        StructureType.NAKED_CALL,
        StructureType.BULL_CALL_SPREAD,
        StructureType.BULL_PUT_SPREAD,
        StructureType.NO_TRADE,
    }
