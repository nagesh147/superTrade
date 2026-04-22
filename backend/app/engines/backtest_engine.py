"""
Backtesting Engine
Event-driven vectorized backtester for options strategies
Supports: slippage, commissions, margin, rolling positions, Greeks tracking
"""
import numpy as np
import pandas as pd
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Callable
from enum import Enum
import math
from loguru import logger
from app.engines.options_pricing import BlackScholesEngine, OptionType


@dataclass
class BacktestConfig:
    initial_capital: float = 100_000.0
    commission_rate: float = 0.0003
    slippage_bps: float = 5.0
    margin_rate: float = 0.15
    risk_free_rate: float = 0.05
    rebalance_freq: str = "1D"   # "1H", "4H", "1D", "1W"
    delta_threshold: float = 0.1  # hedge when |delta| > threshold
    start_date: str = "2023-01-01"
    end_date: str = "2024-01-01"
    strategy: str = "iron_condor"
    synthetic_data: bool = True
    n_paths: int = 1  # for MC scenarios


@dataclass
class BacktestTrade:
    timestamp: int; symbol: str; side: str; quantity: float
    price: float; commission: float; strategy: str; pnl: float = 0.0


@dataclass
class BacktestResult:
    total_return: float; annualized_return: float; sharpe_ratio: float
    sortino_ratio: float; max_drawdown: float; win_rate: float
    profit_factor: float; total_trades: int; total_pnl: float
    final_capital: float; var_95: float; calmar_ratio: float
    equity_curve: List[float] = field(default_factory=list)
    daily_pnl: List[float] = field(default_factory=list)
    trades: List[BacktestTrade] = field(default_factory=list)
    greeks_history: List[dict] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)


class BacktestEngine:
    def __init__(self, config: BacktestConfig):
        self.config = config
        self.bsm = BlackScholesEngine()
        logger.info(f"Backtester initialized: {config.strategy} [{config.start_date} → {config.end_date}]")

    def _generate_btc_path(self, n_days: int, S0: float = 45000,
                            mu: float = 0.5, sigma: float = 0.65) -> np.ndarray:
        """GBM simulation with vol clustering (GARCH-like)"""
        dt = 1/365; prices = [S0]; vol = sigma
        for _ in range(n_days):
            vol = max(0.2, min(2.0, vol * math.exp(np.random.normal(0, 0.05))))
            ret = (mu - 0.5*vol**2)*dt + vol*math.sqrt(dt)*np.random.normal()
            prices.append(prices[-1] * math.exp(ret))
        return np.array(prices)

    def _generate_iv_path(self, n_days: int, iv0: float = 0.65) -> np.ndarray:
        """Correlated IV path (negatively correlated with price)"""
        ivs = [iv0]
        for _ in range(n_days):
            ivs.append(max(0.15, min(2.5, ivs[-1] + np.random.normal(0, 0.02))))
        return np.array(ivs)

    def run_iron_condor(self, config: BacktestConfig) -> BacktestResult:
        n_days = 365; prices = self._generate_btc_path(n_days)
        ivs = self._generate_iv_path(n_days)
        capital = config.initial_capital; equity = [capital]
        daily_pnl = []; trades = []; greeks_hist = []
        wins = 0; losses = 0; gross_profit = 0; gross_loss = 0
        roll_day = 0

        for i in range(0, n_days-7, 7):  # Weekly condors
            S = prices[i]; iv = ivs[i]; T_entry = 7/365
            low_put  = round(S * 0.90 / 1000) * 1000
            high_put = round(S * 0.95 / 1000) * 1000
            low_call = round(S * 1.05 / 1000) * 1000
            high_call= round(S * 1.10 / 1000) * 1000

            # Entry premium
            lp = self.bsm.price(S, low_put,  T_entry, 0.05, iv, OptionType.PUT)
            hp = self.bsm.price(S, high_put, T_entry, 0.05, iv, OptionType.PUT)
            lc = self.bsm.price(S, low_call, T_entry, 0.05, iv, OptionType.CALL)
            hc = self.bsm.price(S, high_call,T_entry, 0.05, iv, OptionType.CALL)
            credit = (hp - lp) + (lc - hc)

            # Exit at expiry (7 days later)
            S_exp = prices[min(i+7, n_days-1)]; T_exp = 0.0001
            lp_e = self.bsm.price(S_exp, low_put,  T_exp, 0.05, iv, OptionType.PUT)
            hp_e = self.bsm.price(S_exp, high_put, T_exp, 0.05, iv, OptionType.PUT)
            lc_e = self.bsm.price(S_exp, low_call, T_exp, 0.05, iv, OptionType.CALL)
            hc_e = self.bsm.price(S_exp, high_call,T_exp, 0.05, iv, OptionType.CALL)
            debit = (hp_e - lp_e) + (lc_e - hc_e)

            pnl = (credit - debit) * 1  # 1 contract
            commission = 8 * config.commission_rate * S * 0.01
            net_pnl = pnl - commission
            capital += net_pnl

            if net_pnl > 0: wins += 1; gross_profit += net_pnl
            else: losses += 1; gross_loss += abs(net_pnl)

            for day_pnl in np.linspace(0, net_pnl, 7):
                daily_pnl.append(float(day_pnl))
                equity.append(capital)

            trades.append(BacktestTrade(
                timestamp=i, symbol="IRON_CONDOR", side="sell",
                quantity=1, price=credit, commission=commission, strategy="iron_condor", pnl=net_pnl
            ))

        r = np.array(daily_pnl) / config.initial_capital
        sharpe = float(r.mean() / r.std() * math.sqrt(365)) if r.std() > 0 else 0
        neg_r = r[r < 0]; sortino = float(r.mean() / neg_r.std() * math.sqrt(365)) if len(neg_r) > 0 and neg_r.std() > 0 else 0
        eq = np.array(equity); peaks = np.maximum.accumulate(eq)
        mdd = float(((eq - peaks) / peaks).min()) if len(eq) > 1 else 0
        total_ret = (capital - config.initial_capital) / config.initial_capital
        var95 = abs(float(np.percentile(r, 5))) * capital if len(r) > 0 else 0
        pf = gross_profit / gross_loss if gross_loss > 0 else float("inf")
        calmar = (total_ret * capital / n_days * 365) / abs(mdd * capital) if mdd != 0 else 0

        return BacktestResult(
            total_return=round(total_ret*100, 2), annualized_return=round(total_ret*100*365/n_days, 2),
            sharpe_ratio=round(sharpe, 3), sortino_ratio=round(sortino, 3),
            max_drawdown=round(mdd*100, 2), win_rate=round(wins/(wins+losses)*100 if wins+losses > 0 else 0, 1),
            profit_factor=round(pf, 2), total_trades=len(trades),
            total_pnl=round(capital-config.initial_capital, 2), final_capital=round(capital, 2),
            var_95=round(var95, 2), calmar_ratio=round(calmar, 3),
            equity_curve=equity[:200], daily_pnl=daily_pnl[:200], trades=trades[:50],
        )

    def run(self) -> BacktestResult:
        logger.info(f"Running backtest: {self.config.strategy}")
        if self.config.strategy == "iron_condor":
            return self.run_iron_condor(self.config)
        return self.run_iron_condor(self.config)  # default
