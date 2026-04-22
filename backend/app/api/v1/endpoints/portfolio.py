from fastapi import APIRouter, Request

router = APIRouter()

@router.get("/summary")
async def portfolio_summary(request: Request):
    oms = request.app.state.oms
    market = request.app.state.market
    spot = market.get_spot()
    summary = oms.portfolio_summary()
    portfolio_value = summary["cash"] + sum(
        qty * spot for sym, qty in summary["positions"].items() if "PERP" in sym or "BTC" in sym
    )
    return {**summary, "portfolio_value": portfolio_value, "spot": spot, "paper_mode": oms.paper_mode}

@router.get("/risk")
async def portfolio_risk(request: Request):
    market = request.app.state.market
    risk = request.app.state.risk
    oms = request.app.state.oms
    import random
    spot = market.get_spot()
    returns = [random.gauss(0.001, 0.03) for _ in range(100)]
    equity = [100000 * (1 + sum(returns[:i])) for i in range(len(returns))]
    positions = []
    report = risk.full_risk_report(positions, 100000, spot, returns, equity, 
                                    random.gauss(100, 500), 15000, 100000)
    return {
        "delta": report.portfolio_greeks.net_delta,
        "gamma": report.portfolio_greeks.net_gamma,
        "vega": report.portfolio_greeks.net_vega,
        "theta": report.portfolio_greeks.net_theta,
        "var_95": report.var_95, "var_99": report.var_99,
        "sharpe": report.sharpe_ratio, "max_drawdown": report.max_drawdown,
        "risk_level": report.risk_level, "alerts": report.alerts,
        "leverage": report.leverage, "daily_pnl": report.daily_pnl,
    }
