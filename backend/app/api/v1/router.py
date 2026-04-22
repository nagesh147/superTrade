from fastapi import APIRouter
from app.api.v1.endpoints import market, orders, portfolio, strategies, backtest, analytics, ws

api_router = APIRouter()
api_router.include_router(market.router,     prefix="/market",    tags=["Market Data"])
api_router.include_router(orders.router,     prefix="/orders",    tags=["Orders"])
api_router.include_router(portfolio.router,  prefix="/portfolio", tags=["Portfolio"])
api_router.include_router(strategies.router, prefix="/strategies",tags=["Strategies"])
api_router.include_router(backtest.router,   prefix="/backtest",  tags=["Backtesting"])
api_router.include_router(analytics.router,  prefix="/analytics", tags=["Analytics"])
api_router.include_router(ws.router,         prefix="/ws",        tags=["WebSocket"])
