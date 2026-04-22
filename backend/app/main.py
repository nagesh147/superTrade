"""
superTrade - FastAPI Application
"""
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from loguru import logger
import uvicorn

from app.core.config import settings
from app.api.v1.router import api_router
from app.engines.market_data_engine import MarketDataEngine
from app.engines.risk_manager import RiskManager
from app.engines.order_manager import OrderManager
from app.engines.strategy_engine import StrategyEngine

# Global engine instances (singleton pattern for this app)
market_engine: MarketDataEngine = None
risk_engine: RiskManager = None
oms: OrderManager = None
strategy_engine: StrategyEngine = None
feed_task: asyncio.Task = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global market_engine, risk_engine, oms, strategy_engine, feed_task
    logger.info("=== superTrade Starting ===")
    
    # Initialize engines
    market_engine = MarketDataEngine({
        "ws_url": settings.DERIBIT_WS_URL,
        "api_key": settings.DERIBIT_API_KEY,
        "api_secret": settings.DERIBIT_API_SECRET,
        "paper_mode": settings.PAPER_TRADING,
    })
    risk_engine = RiskManager({
        "max_delta": settings.MAX_DELTA_EXPOSURE,
        "max_vega": settings.MAX_VEGA_EXPOSURE,
        "max_daily_loss": settings.MAX_DAILY_LOSS_USD,
        "max_leverage": settings.MAX_PORTFOLIO_LEVERAGE,
    })
    oms = OrderManager(paper_mode=settings.PAPER_TRADING)
    strategy_engine = StrategyEngine(r=settings.RISK_FREE_RATE)

    # Connect and start data feed
    await market_engine.connect()
    if settings.PAPER_TRADING:
        feed_task = asyncio.create_task(market_engine.start_paper_feed())

    # Attach to app state
    app.state.market = market_engine
    app.state.risk = risk_engine
    app.state.oms = oms
    app.state.strategy = strategy_engine

    logger.info(f"All engines initialized | Paper mode: {settings.PAPER_TRADING}")
    yield

    # Shutdown
    logger.info("Shutting down engines...")
    if feed_task: feed_task.cancel()
    await market_engine.stop()
    logger.info("=== Shutdown complete ===")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Professional-grade Crypto Options Algorithmic Trading System",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

# Middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
async def health():
    return {"status": "ok", "version": settings.APP_VERSION,
            "paper_mode": settings.PAPER_TRADING,
            "market_connected": market_engine.is_connected() if market_engine else False}


if __name__ == "__main__":
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT,
                reload=settings.RELOAD, log_level=settings.LOG_LEVEL.lower())
