"""
Strategy Engine - Pluggable options trading strategies
Strategies: Delta Neutral, Iron Condor, Straddle/Strangle, Covered Call, Bull/Bear Spreads,
            Butterfly, Calendar Spread, Volatility Arbitrage
"""
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Dict, Any
import math
from app.engines.options_pricing import BlackScholesEngine, OptionType


class StrategyType(str, Enum):
    DELTA_NEUTRAL    = "delta_neutral"
    IRON_CONDOR      = "iron_condor"
    STRADDLE         = "straddle"
    STRANGLE         = "strangle"
    COVERED_CALL     = "covered_call"
    PROTECTIVE_PUT   = "protective_put"
    BULL_CALL_SPREAD = "bull_call_spread"
    BEAR_PUT_SPREAD  = "bear_put_spread"
    BUTTERFLY        = "butterfly"
    CALENDAR_SPREAD  = "calendar_spread"
    VOL_ARB          = "volatility_arb"


@dataclass
class Leg:
    option_type: OptionType
    strike: float
    expiry_T: float   # years to expiry
    quantity: float   # +ve = long, -ve = short
    is_spot: bool = False


@dataclass
class StrategySignal:
    strategy: StrategyType
    legs: List[Leg]
    max_profit: float
    max_loss: float
    breakevens: List[float]
    net_premium: float
    net_delta: float
    net_gamma: float
    net_vega: float
    net_theta: float
    rationale: str


class StrategyEngine:
    def __init__(self, r: float = 0.05):
        self.r = r
        self.bsm = BlackScholesEngine()

    def _price_leg(self, S, leg: Leg, sigma: float) -> tuple:
        if leg.is_spot:
            return S, {"delta": 1.0, "gamma": 0.0, "theta": 0.0, "vega": 0.0, "rho": 0.0}
        result = self.bsm.full(S, leg.strike, leg.expiry_T, self.r, sigma, leg.option_type)
        g = result.greeks
        return result.price, {"delta":g.delta,"gamma":g.gamma,"theta":g.theta,"vega":g.vega,"rho":g.rho}

    def _aggregate(self, S, legs, sigma):
        net_premium = net_delta = net_gamma = net_vega = net_theta = 0.0
        for leg in legs:
            p, g = self._price_leg(S, leg, sigma)
            net_premium += p * leg.quantity
            net_delta   += g["delta"] * leg.quantity
            net_gamma   += g["gamma"] * leg.quantity
            net_vega    += g["vega"]  * leg.quantity
            net_theta   += g["theta"] * leg.quantity
        return net_premium, net_delta, net_gamma, net_vega, net_theta

    def iron_condor(self, S, sigma, T, low_put, high_put, low_call, high_call) -> StrategySignal:
        legs = [
            Leg(OptionType.PUT,  low_put,   T,  1),   # Long lower put
            Leg(OptionType.PUT,  high_put,  T, -1),   # Short higher put
            Leg(OptionType.CALL, low_call,  T, -1),   # Short lower call
            Leg(OptionType.CALL, high_call, T,  1),   # Long higher call
        ]
        net_prem, nd, ng, nv, nt = self._aggregate(S, legs, sigma)
        credit = -net_prem
        spread_w = high_put - low_put
        max_loss = spread_w - credit
        return StrategySignal(
            strategy=StrategyType.IRON_CONDOR, legs=legs,
            max_profit=credit, max_loss=max_loss,
            breakevens=[high_put - credit, low_call + credit],
            net_premium=net_prem, net_delta=nd, net_gamma=ng, net_vega=nv, net_theta=nt,
            rationale=f"Iron Condor: collect ${credit:.2f} premium; profit if asset stays [{high_put:.0f}, {low_call:.0f}]"
        )

    def straddle(self, S, sigma, T, atm_offset=0) -> StrategySignal:
        K = round(S * (1 + atm_offset), -2)
        legs = [Leg(OptionType.CALL, K, T, 1), Leg(OptionType.PUT, K, T, 1)]
        net_prem, nd, ng, nv, nt = self._aggregate(S, legs, sigma)
        return StrategySignal(
            strategy=StrategyType.STRADDLE, legs=legs,
            max_profit=float("inf"), max_loss=net_prem,
            breakevens=[K - net_prem, K + net_prem],
            net_premium=net_prem, net_delta=nd, net_gamma=ng, net_vega=nv, net_theta=nt,
            rationale=f"Long Straddle at K={K}: profit from large asset move either direction. Cost: ${net_prem:.2f}"
        )

    def strangle(self, S, sigma, T, put_K, call_K) -> StrategySignal:
        legs = [Leg(OptionType.CALL, call_K, T, 1), Leg(OptionType.PUT, put_K, T, 1)]
        net_prem, nd, ng, nv, nt = self._aggregate(S, legs, sigma)
        return StrategySignal(
            strategy=StrategyType.STRANGLE, legs=legs,
            max_profit=float("inf"), max_loss=net_prem,
            breakevens=[put_K - net_prem, call_K + net_prem],
            net_premium=net_prem, net_delta=nd, net_gamma=ng, net_vega=nv, net_theta=nt,
            rationale=f"Long Strangle ({put_K}/{call_K}): cheaper than straddle, needs bigger move"
        )

    def covered_call(self, S, sigma, T, call_K) -> StrategySignal:
        legs = [Leg(OptionType.CALL, call_K, T, -1, is_spot=False), Leg(OptionType.CALL, 0, T, 1, is_spot=True)]
        call_p, call_g = self._price_leg(S, legs[0], sigma)
        premium_recv = call_p
        return StrategySignal(
            strategy=StrategyType.COVERED_CALL, legs=legs,
            max_profit=call_K - S + premium_recv, max_loss=S - premium_recv,
            breakevens=[S - premium_recv],
            net_premium=-premium_recv, net_delta=1 + call_g["delta"]*(-1),
            net_gamma=0, net_vega=call_g["vega"]*(-1), net_theta=call_g["theta"]*(-1),
            rationale=f"Covered Call at {call_K}: collect ${premium_recv:.2f} income, cap upside"
        )

    def bull_call_spread(self, S, sigma, T, low_K, high_K) -> StrategySignal:
        legs = [Leg(OptionType.CALL, low_K, T, 1), Leg(OptionType.CALL, high_K, T, -1)]
        net_prem, nd, ng, nv, nt = self._aggregate(S, legs, sigma)
        return StrategySignal(
            strategy=StrategyType.BULL_CALL_SPREAD, legs=legs,
            max_profit=(high_K - low_K) - net_prem, max_loss=net_prem,
            breakevens=[low_K + net_prem],
            net_premium=net_prem, net_delta=nd, net_gamma=ng, net_vega=nv, net_theta=nt,
            rationale=f"Bull Call Spread {low_K}/{high_K}: limited risk bullish bet"
        )

    def butterfly(self, S, sigma, T, low_K, mid_K, high_K) -> StrategySignal:
        legs = [
            Leg(OptionType.CALL, low_K,  T,  1),
            Leg(OptionType.CALL, mid_K,  T, -2),
            Leg(OptionType.CALL, high_K, T,  1),
        ]
        net_prem, nd, ng, nv, nt = self._aggregate(S, legs, sigma)
        return StrategySignal(
            strategy=StrategyType.BUTTERFLY, legs=legs,
            max_profit=(mid_K - low_K) - net_prem, max_loss=net_prem,
            breakevens=[low_K + net_prem, high_K - net_prem],
            net_premium=net_prem, net_delta=nd, net_gamma=ng, net_vega=nv, net_theta=nt,
            rationale=f"Butterfly {low_K}/{mid_K}/{high_K}: profit if asset pins near {mid_K}"
        )

    def delta_hedge_quantity(self, portfolio_delta: float, spot: float) -> float:
        """How much spot crypto to trade to neutralize delta"""
        return -portfolio_delta  # sell delta amount of crypto

    def select_strategy(self, spot: float, iv: float, iv_rank: float,
                        market_bias: str = "neutral") -> StrategyType:
        """Rule-based strategy selection based on market conditions"""
        if iv_rank > 0.7:  # High IV rank - sell vol
            if market_bias == "neutral":
                return StrategyType.IRON_CONDOR
            elif market_bias == "bearish":
                return StrategyType.BEAR_PUT_SPREAD
            else:
                return StrategyType.COVERED_CALL
        elif iv_rank < 0.3:  # Low IV rank - buy vol
            return StrategyType.STRADDLE
        else:
            if market_bias == "bullish":
                return StrategyType.BULL_CALL_SPREAD
            elif market_bias == "bearish":
                return StrategyType.BEAR_PUT_SPREAD
            return StrategyType.IRON_CONDOR
