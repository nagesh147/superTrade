"""
Options Pricing Engine - Black-Scholes, Monte Carlo, Binomial Tree + Full Greeks
"""
import numpy as np
from scipy.stats import norm
from scipy.optimize import brentq
from dataclasses import dataclass
from enum import Enum
from typing import Optional
import math


class OptionType(str, Enum):
    CALL = "call"
    PUT = "put"


@dataclass
class OptionGreeks:
    delta: float; gamma: float; theta: float; vega: float
    rho: float; vanna: float; volga: float; charm: float


@dataclass
class OptionResult:
    price: float; greeks: OptionGreeks; model: str
    intrinsic_value: float; time_value: float


class BlackScholesEngine:
    @staticmethod
    def _d1(S, K, T, r, sigma, q=0.0):
        return (math.log(S/K) + (r - q + 0.5*sigma**2)*T) / (sigma*math.sqrt(T))

    @staticmethod
    def _d2(S, K, T, r, sigma, q=0.0):
        return BlackScholesEngine._d1(S,K,T,r,sigma,q) - sigma*math.sqrt(T)

    @classmethod
    def price(cls, S, K, T, r, sigma, opt_type: OptionType, q=0.0):
        if T <= 0:
            return max(0, S-K) if opt_type == OptionType.CALL else max(0, K-S)
        d1 = cls._d1(S,K,T,r,sigma,q); d2 = d1 - sigma*math.sqrt(T)
        if opt_type == OptionType.CALL:
            return S*math.exp(-q*T)*norm.cdf(d1) - K*math.exp(-r*T)*norm.cdf(d2)
        return K*math.exp(-r*T)*norm.cdf(-d2) - S*math.exp(-q*T)*norm.cdf(-d1)

    @classmethod
    def greeks(cls, S, K, T, r, sigma, opt_type: OptionType, q=0.0):
        if T <= 0:
            return OptionGreeks(0,0,0,0,0,0,0,0)
        d1 = cls._d1(S,K,T,r,sigma,q); d2 = d1 - sigma*math.sqrt(T)
        sqT = math.sqrt(T); eqT = math.exp(-q*T); erT = math.exp(-r*T); pd1 = norm.pdf(d1)
        delta = eqT*norm.cdf(d1) if opt_type==OptionType.CALL else eqT*(norm.cdf(d1)-1)
        gamma = eqT*pd1/(S*sigma*sqT)
        t_base = -(S*eqT*pd1*sigma)/(2*sqT)
        theta = (t_base - r*K*erT*norm.cdf(d2) + q*S*eqT*norm.cdf(d1))/365 if opt_type==OptionType.CALL \
                else (t_base + r*K*erT*norm.cdf(-d2) - q*S*eqT*norm.cdf(-d1))/365
        vega = S*eqT*pd1*sqT/100
        rho = K*T*erT*norm.cdf(d2)/100 if opt_type==OptionType.CALL else -K*T*erT*norm.cdf(-d2)/100
        vanna = -eqT*pd1*d2/sigma
        volga = vega*d1*d2/sigma
        charm_base = eqT*pd1*(2*(r-q)*T - d2*sigma*sqT)/(2*T*sigma*sqT)
        charm = (-charm_base + q*eqT*norm.cdf(d1))/365 if opt_type==OptionType.CALL \
                else (-charm_base - q*eqT*norm.cdf(-d1))/365
        return OptionGreeks(round(delta,6),round(gamma,6),round(theta,6),round(vega,6),
                           round(rho,6),round(vanna,6),round(volga,6),round(charm,6))

    @classmethod
    def implied_vol(cls, mkt_price, S, K, T, r, opt_type: OptionType, q=0.0):
        if T <= 0 or mkt_price <= 0: return None
        try:
            return brentq(lambda s: cls.price(S,K,T,r,s,opt_type,q) - mkt_price, 1e-6, 20.0, xtol=1e-6)
        except: return None

    @classmethod
    def full(cls, S, K, T, r, sigma, opt_type: OptionType, q=0.0):
        p = cls.price(S,K,T,r,sigma,opt_type,q)
        g = cls.greeks(S,K,T,r,sigma,opt_type,q)
        intrin = max(0, S-K) if opt_type==OptionType.CALL else max(0, K-S)
        return OptionResult(round(p,4), g, "black_scholes", round(intrin,4), round(p-intrin,4))


class MonteCarloEngine:
    @staticmethod
    def price(S, K, T, r, sigma, opt_type: OptionType, q=0.0,
              n_paths=100_000, n_steps=252, antithetic=True):
        dt = T/n_steps; discount = math.exp(-r*T)
        n_half = n_paths//2
        Z = np.random.standard_normal((n_half, n_steps))
        if antithetic: Z = np.concatenate([Z, -Z], axis=0)
        log_S = np.log(S) + np.cumsum((r-q-0.5*sigma**2)*dt + sigma*math.sqrt(dt)*Z, axis=1)
        ST = np.exp(log_S[:,-1])
        payoffs = np.maximum(ST-K,0) if opt_type==OptionType.CALL else np.maximum(K-ST,0)
        return round(float(discount*np.mean(payoffs)), 4)


class BinomialEngine:
    @staticmethod
    def price(S, K, T, r, sigma, opt_type: OptionType, q=0.0, steps=500, american=True):
        dt = T/steps; u = math.exp(sigma*math.sqrt(dt)); d = 1/u
        p = (math.exp((r-q)*dt) - d)/(u-d); disc = math.exp(-r*dt)
        prices = S * d**np.arange(steps,-1,-1) * u**np.arange(0,steps+1)
        vals = np.maximum(prices-K,0) if opt_type==OptionType.CALL else np.maximum(K-prices,0)
        for i in range(steps-1,-1,-1):
            prices = prices[1:]/u
            hold = disc*(p*vals[1:] + (1-p)*vals[:-1])
            if american:
                ex = np.maximum(prices-K,0) if opt_type==OptionType.CALL else np.maximum(K-prices,0)
                vals = np.maximum(hold, ex)
            else: vals = hold
        return round(float(vals[0]), 4)


def build_vol_surface(strikes, expiries, spot, r, market_prices, opt_types):
    """Build implied volatility surface from market quotes"""
    surface = {}
    for T, K, mkt_p, ot in zip(expiries, strikes, market_prices, opt_types):
        iv = BlackScholesEngine.implied_vol(mkt_p, spot, K, T, r, ot)
        surface[(T, K)] = iv
    return surface
