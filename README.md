# ⚡ APEX — BTC/USD Options Algorithmic Trading System

> Professional-grade algorithmic options trading platform for Bitcoin. Full-stack, production-ready, runs locally or via Docker.

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│                    APEX TRADING SYSTEM               │
├─────────────────────────────────────────────────────┤
│  FRONTEND (React + TypeScript + Vite)               │
│  ├── Dashboard: Real-time PnL, Greeks, Risk         │
│  ├── Options Chain: Live IV surface                 │
│  ├── Strategy Builder: Analyze & execute strategies │
│  ├── Backtester: Historical simulation engine       │
│  └── Orders: Manual + automated order management   │
├─────────────────────────────────────────────────────┤
│  BACKEND (FastAPI + Python)                         │
│  ├── Options Pricing Engine (BSM / MC / Binomial)  │
│  ├── Strategy Engine (8 strategies)                │
│  ├── Risk Manager (Greeks, VaR, limits)            │
│  ├── Order Management System (OMS)                 │
│  ├── Market Data Engine (WS + paper feed)          │
│  └── Backtesting Engine (event-driven)             │
├─────────────────────────────────────────────────────┤
│  INFRASTRUCTURE                                     │
│  ├── PostgreSQL + TimescaleDB (time-series)         │
│  ├── Redis (real-time cache + pub/sub)              │
│  ├── WebSocket real-time feed                      │
│  └── Docker Compose (all-in-one deployment)        │
└─────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Option 1: Local Dev (Recommended)

**Prerequisites:** Python 3.11+, Node 20+, (optional: PostgreSQL, Redis)

```bash
# 1. Clone and enter the project
cd superTrade

# 2. One-command start (paper trading mode, no DB needed)
bash infra/scripts/start.sh
```

**Or manually:**

```bash
# Terminal 1 — Backend
cd backend
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000

# Terminal 2 — Frontend
cd frontend
npm install
cp .env.example .env
npm run dev
```

Open: http://localhost:5173

### Option 2: Docker (Full Stack)

```bash
docker-compose up --build
```

Open: http://localhost (via nginx)

---

## 📁 Project Structure

```
superTrade/
├── backend/
│   ├── app/
│   │   ├── core/           # Config, database, security
│   │   ├── engines/        # Trading engines (pricing, risk, OMS, strategy, backtest)
│   │   ├── api/v1/         # FastAPI REST + WebSocket endpoints
│   │   ├── models/         # SQLAlchemy models
│   │   ├── schemas/        # Pydantic schemas
│   │   └── services/       # Exchange integrations, notifications
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/     # Reusable UI: charts, panels, forms
│   │   ├── pages/          # Dashboard, Chain, Strategy, Backtest, Orders, Risk
│   │   ├── hooks/          # React Query data hooks + WebSocket
│   │   ├── store/          # Zustand global state
│   │   ├── types/          # TypeScript interfaces
│   │   └── utils/          # API client, formatters
│   ├── package.json
│   └── Dockerfile
├── infra/
│   ├── docker/
│   ├── nginx/nginx.conf
│   └── scripts/start.sh
├── docker-compose.yml
└── README.md
```

---

## ⚙️ Configuration (.env)

```env
# Paper trading (no real money, simulated feed)
PAPER_TRADING=true

# Live trading (Deribit testnet first!)
DERIBIT_API_KEY=your_key
DERIBIT_API_SECRET=your_secret
DERIBIT_TESTNET=true   # Set false for mainnet

# Risk limits
MAX_DELTA_EXPOSURE=1.0
MAX_DAILY_LOSS_USD=1000
MAX_PORTFOLIO_LEVERAGE=3.0
```

---

## 📐 Engines & Features

### Options Pricing Engine
- **Black-Scholes-Merton** with full Greeks (Δ, Γ, Θ, V, ρ, Vanna, Volga, Charm)
- **Monte Carlo** with antithetic variates (100K paths)
- **Binomial Tree** (CRR, American-style exercise)
- **Implied Volatility** solver (Brent's method)
- **IV Surface** calibration (SVI parametrization)

### Strategies
| Strategy | Type | Description |
|---|---|---|
| Iron Condor | Neutral | Sell OTM put+call spreads |
| Long Straddle | Long Vol | ATM call+put, big move play |
| Long Strangle | Long Vol | OTM call+put, cheaper |
| Covered Call | Income | BTC holding + OTM call |
| Bull Call Spread | Bullish | Limited risk directional |
| Bear Put Spread | Bearish | Limited risk directional |
| Butterfly | Neutral | Pin risk at target strike |
| Delta Neutral | Neutral | Continuous delta hedging |

### Risk Management
- Real-time Greeks aggregation
- Value at Risk (95% + 99% VaR)
- Expected Shortfall (CVaR)
- Maximum Drawdown tracking
- Sharpe / Sortino / Calmar ratios
- Automated kill-switch on limit breach

### Backtesting
- Event-driven backtester
- Realistic slippage + commission modeling
- Position rolling at expiry
- Greeks tracking over time
- Full performance statistics

---

## 🔌 API Reference

API docs auto-generated at: http://localhost:8000/api/docs

| Endpoint | Description |
|---|---|
| GET /api/v1/market/ticker | Live spot + IV |
| GET /api/v1/market/options-chain | Full options chain |
| POST /api/v1/strategies/analyze | Analyze strategy |
| GET /api/v1/strategies/recommend | AI strategy recommendation |
| POST /api/v1/orders/create | Place order |
| GET /api/v1/portfolio/risk | Portfolio risk report |
| POST /api/v1/backtest/run | Run backtest |
| WS /api/v1/ws/feed | Real-time price feed |

---

## ⚠️ Disclaimer

This system is for educational and research purposes. Paper trading mode is enabled by default.
**Never risk money you cannot afford to lose.** Options trading involves substantial risk.
Always test thoroughly on testnet before any live deployment.

---

## 📦 Tech Stack

**Backend:** FastAPI, SQLAlchemy, asyncpg, WebSockets, NumPy, SciPy, CCXT, Loguru  
**Frontend:** React 18, TypeScript, Vite, Tailwind CSS, Zustand, React Query, Recharts, Framer Motion  
**Infrastructure:** PostgreSQL + TimescaleDB, Redis, Docker, Nginx  
