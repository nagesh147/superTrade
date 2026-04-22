from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional, List


class Settings(BaseSettings):
    APP_NAME: str = "superTrade"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"
    SECRET_KEY: str = "changeme-use-strong-secret-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    ALGORITHM: str = "HS256"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    ALLOWED_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/supertrade"
    REDIS_URL: str = "redis://localhost:6379/0"
    DERIBIT_API_KEY: Optional[str] = None
    DERIBIT_API_SECRET: Optional[str] = None
    DERIBIT_TESTNET: bool = True
    DERIBIT_WS_URL: str = "wss://test.deribit.com/ws/api/v2"
    BINANCE_API_KEY: Optional[str] = None
    BINANCE_API_SECRET: Optional[str] = None
    MAX_POSITION_SIZE_USD: float = 10000.0
    MAX_DELTA_EXPOSURE: float = 1.0
    MAX_VEGA_EXPOSURE: float = 5000.0
    MAX_DAILY_LOSS_USD: float = 1000.0
    MAX_PORTFOLIO_LEVERAGE: float = 3.0
    RISK_FREE_RATE: float = 0.05
    PRICING_MODEL: str = "black_scholes"
    REBALANCE_THRESHOLD_DELTA: float = 0.1
    MARKET_DATA_INTERVAL_MS: int = 500
    LOG_LEVEL: str = "INFO"
    PAPER_TRADING: bool = True

    class Config:
        env_file = ".env"

settings = Settings()
