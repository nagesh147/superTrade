"""
Risk Management Engine
Real-time portfolio risk monitoring, Greeks aggregation, VaR, stop-loss enforcement
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from enum import Enum
import numpy as np
from loguru import logger


class RiskLevel(str, Enum):
    SAFE = "safe"
    WARNING = "warning"
    CRITICAL = "critical"
    BREACH = "breach"


@dataclass
class PortfolioGreeks:
    net_delta: float = 0.0
    net_gamma: float = 0.0
    net_theta: float = 0.0
    net_vega: float = 0.0
    net_rho: float = 0.0
    dollar_delta: float = 0.0
    dollar_gamma: float = 0.0
    dollar_vega: float = 0.0


@dataclass
class RiskMetrics:
    portfolio_greeks: PortfolioGreeks
    var_95: float          # 1-day 95% VaR in USD
    var_99: float          # 1-day 99% VaR in USD
    expected_shortfall: float
    max_drawdown: float
    sharpe_ratio: float
    daily_pnl: float
    unrealized_pnl: float
    total_notional: float
    leverage: float
    margin_used: float
    margin_available: float
    risk_level: RiskLevel
    alerts: List[str] = field(default_factory=list)


class RiskManager:
    def __init__(self, config: dict):
        self.max_delta = config.get("max_delta", 1.0)
        self.max_vega = config.get("max_vega", 5000.0)
        self.max_daily_loss = config.get("max_daily_loss", 1000.0)
        self.max_leverage = config.get("max_leverage", 3.0)
        self.min_cash_reserve = config.get("min_cash_reserve", 0.20)
        self.pnl_history: List[float] = []
        self.position_history: List[float] = []

    def compute_portfolio_greeks(self, positions: List[dict], spot: float) -> PortfolioGreeks:
        pg = PortfolioGreeks()
        for pos in positions:
            qty = pos["quantity"]
            g = pos["greeks"]
            pg.net_delta += g["delta"] * qty
            pg.net_gamma += g["gamma"] * qty
            pg.net_theta += g["theta"] * qty
            pg.net_vega  += g["vega"]  * qty
            pg.net_rho   += g["rho"]   * qty
        pg.dollar_delta = pg.net_delta * spot
        pg.dollar_gamma = pg.net_gamma * spot**2 * 0.01
        pg.dollar_vega  = pg.net_vega  * 100
        return pg

    def compute_var(self, returns: List[float], portfolio_value: float,
                    confidence_95=0.95, confidence_99=0.99) -> tuple:
        if len(returns) < 30:
            return 0.0, 0.0
        r = np.array(returns)
        var_95 = abs(np.percentile(r, (1-confidence_95)*100)) * portfolio_value
        var_99 = abs(np.percentile(r, (1-confidence_99)*100)) * portfolio_value
        return round(var_95, 2), round(var_99, 2)

    def compute_expected_shortfall(self, returns: List[float], portfolio_value: float, confidence=0.95) -> float:
        if len(returns) < 30: return 0.0
        r = np.array(returns)
        cutoff = np.percentile(r, (1-confidence)*100)
        es = abs(r[r <= cutoff].mean()) * portfolio_value if len(r[r <= cutoff]) > 0 else 0.0
        return round(es, 2)

    def compute_max_drawdown(self, equity_curve: List[float]) -> float:
        if len(equity_curve) < 2: return 0.0
        peaks = np.maximum.accumulate(equity_curve)
        drawdowns = (np.array(equity_curve) - peaks) / peaks
        return round(float(drawdowns.min()), 4)

    def compute_sharpe(self, returns: List[float], risk_free=0.05/365) -> float:
        if len(returns) < 30: return 0.0
        r = np.array(returns)
        excess = r - risk_free
        return round(float(excess.mean() / excess.std() * np.sqrt(365)), 3) if excess.std() > 0 else 0.0

    def check_risk_limits(self, greeks: PortfolioGreeks, daily_pnl: float,
                          leverage: float, margin_used_pct: float) -> tuple:
        alerts = []
        level = RiskLevel.SAFE

        if abs(greeks.net_delta) > self.max_delta:
            alerts.append(f"DELTA BREACH: {greeks.net_delta:.3f} > limit {self.max_delta}")
            level = RiskLevel.BREACH
        elif abs(greeks.net_delta) > self.max_delta * 0.8:
            alerts.append(f"Delta warning: {greeks.net_delta:.3f}")
            level = max(level, RiskLevel.WARNING, key=lambda x: ["safe","warning","critical","breach"].index(x))

        if abs(greeks.net_vega) > self.max_vega:
            alerts.append(f"VEGA BREACH: {greeks.net_vega:.1f} > limit {self.max_vega}")
            level = RiskLevel.BREACH

        if daily_pnl < -self.max_daily_loss:
            alerts.append(f"DAILY LOSS LIMIT HIT: ${daily_pnl:.2f}")
            level = RiskLevel.BREACH
        elif daily_pnl < -self.max_daily_loss * 0.75:
            alerts.append(f"Approaching daily loss limit: ${daily_pnl:.2f}")

        if leverage > self.max_leverage:
            alerts.append(f"LEVERAGE BREACH: {leverage:.2f}x > {self.max_leverage}x")
            level = RiskLevel.BREACH

        if margin_used_pct > 0.90:
            alerts.append(f"CRITICAL MARGIN: {margin_used_pct*100:.1f}% used")
            level = RiskLevel.CRITICAL

        return level, alerts

    def full_risk_report(self, positions: List[dict], portfolio_value: float,
                         spot: float, returns: List[float], equity_curve: List[float],
                         daily_pnl: float, margin_used: float, margin_total: float) -> RiskMetrics:
        greeks = self.compute_portfolio_greeks(positions, spot)
        var95, var99 = self.compute_var(returns, portfolio_value)
        es = self.compute_expected_shortfall(returns, portfolio_value)
        mdd = self.compute_max_drawdown(equity_curve)
        sharpe = self.compute_sharpe(returns)
        leverage = portfolio_value / margin_total if margin_total > 0 else 0
        margin_pct = margin_used / margin_total if margin_total > 0 else 0
        risk_level, alerts = self.check_risk_limits(greeks, daily_pnl, leverage, margin_pct)
        return RiskMetrics(
            portfolio_greeks=greeks, var_95=var95, var_99=var99,
            expected_shortfall=es, max_drawdown=mdd, sharpe_ratio=sharpe,
            daily_pnl=daily_pnl, unrealized_pnl=sum(p.get("unrealized_pnl",0) for p in positions),
            total_notional=portfolio_value, leverage=round(leverage,2),
            margin_used=margin_used, margin_available=margin_total-margin_used,
            risk_level=risk_level, alerts=alerts,
        )
