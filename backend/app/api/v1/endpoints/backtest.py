from fastapi import APIRouter, Request
from pydantic import BaseModel
from typing import Optional
from app.engines.backtest_engine import BacktestEngine, BacktestConfig

router = APIRouter()

class BacktestRequest(BaseModel):
    strategy: str = "iron_condor"
    initial_capital: float = 100000.0
    commission_rate: float = 0.0003
    start_date: str = "2023-01-01"
    end_date: str = "2024-01-01"
    delta_threshold: float = 0.1

@router.post("/run")
async def run_backtest(req: BacktestRequest):
    config = BacktestConfig(
        initial_capital=req.initial_capital,
        commission_rate=req.commission_rate,
        strategy=req.strategy,
        start_date=req.start_date,
        end_date=req.end_date,
        delta_threshold=req.delta_threshold,
    )
    engine = BacktestEngine(config)
    result = engine.run()
    return {
        "total_return_pct": result.total_return,
        "annualized_return_pct": result.annualized_return,
        "sharpe_ratio": result.sharpe_ratio,
        "sortino_ratio": result.sortino_ratio,
        "max_drawdown_pct": result.max_drawdown,
        "win_rate_pct": result.win_rate,
        "profit_factor": result.profit_factor,
        "total_trades": result.total_trades,
        "total_pnl": result.total_pnl,
        "final_capital": result.final_capital,
        "var_95": result.var_95,
        "calmar_ratio": result.calmar_ratio,
        "equity_curve": result.equity_curve,
        "daily_pnl": result.daily_pnl,
    }
