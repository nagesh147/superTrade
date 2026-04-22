from fastapi import APIRouter, Request
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

class StrategyRequest(BaseModel):
    strategy: str = "iron_condor"
    spot_override: Optional[float] = None
    iv_override: Optional[float] = None
    expiry_days: int = 7
    wing_width_pct: float = 0.05
    quantity: int = 1

@router.get("/list")
async def list_strategies():
    return {"strategies": [
        {"id": "iron_condor",      "name": "Iron Condor",       "type": "neutral",  "description": "Sell OTM put+call spreads, profit from low vol"},
        {"id": "straddle",         "name": "Long Straddle",      "type": "long_vol", "description": "Buy ATM call+put, profit from large moves"},
        {"id": "strangle",         "name": "Long Strangle",      "type": "long_vol", "description": "Buy OTM call+put, cheaper than straddle"},
        {"id": "covered_call",     "name": "Covered Call",       "type": "income",   "description": "Own crypto, sell OTM calls for income"},
        {"id": "bull_call_spread", "name": "Bull Call Spread",   "type": "bullish",  "description": "Limited risk bullish directional bet"},
        {"id": "butterfly",        "name": "Butterfly Spread",   "type": "neutral",  "description": "Profit if asset pins at target strike"},
        {"id": "calendar_spread",  "name": "Calendar Spread",    "type": "neutral",  "description": "Sell near-term, buy far-term, profit from theta"},
        {"id": "delta_neutral",    "name": "Delta Neutral Hedge","type": "neutral",  "description": "Continuously hedge delta with perp/spot"},
    ]}

@router.post("/analyze")
async def analyze_strategy(req: StrategyRequest, request: Request):
    market = request.app.state.market
    se = request.app.state.strategy
    spot = req.spot_override or market.get_spot()
    iv = req.iv_override or market.get_iv()
    T = req.expiry_days / 365

    if req.strategy == "iron_condor":
        w = req.wing_width_pct
        sig = se.iron_condor(spot, iv, T,
                              spot*(1-w*2), spot*(1-w), spot*(1+w), spot*(1+w*2))
    elif req.strategy == "straddle":
        sig = se.straddle(spot, iv, T)
    elif req.strategy == "strangle":
        sig = se.strangle(spot, iv, T, spot*0.93, spot*1.07)
    elif req.strategy == "bull_call_spread":
        sig = se.bull_call_spread(spot, iv, T, spot, spot*1.10)
    elif req.strategy == "butterfly":
        sig = se.butterfly(spot, iv, T, spot*0.95, spot, spot*1.05)
    else:
        sig = se.iron_condor(spot, iv, T, spot*0.90, spot*0.95, spot*1.05, spot*1.10)

    return {
        "strategy": sig.strategy, "net_premium": round(sig.net_premium, 2),
        "max_profit": sig.max_profit if sig.max_profit != float("inf") else "unlimited",
        "max_loss": sig.max_loss if sig.max_loss != float("inf") else "unlimited",
        "breakevens": [round(b, 2) for b in sig.breakevens],
        "greeks": {"delta": round(sig.net_delta, 4), "gamma": round(sig.net_gamma, 6),
                   "vega": round(sig.net_vega, 4), "theta": round(sig.net_theta, 4)},
        "rationale": sig.rationale,
        "legs": [{"type": l.option_type, "strike": l.strike,
                  "qty": l.quantity, "T": l.expiry_T} for l in sig.legs],
    }

@router.get("/recommend")
async def recommend_strategy(request: Request):
    market = request.app.state.market
    se = request.app.state.strategy
    spot = market.get_spot(); iv = market.get_iv()
    iv_rank = min(1.0, max(0.0, (iv - 0.30) / (1.50 - 0.30)))
    rec = se.select_strategy(spot, iv, iv_rank, "neutral")
    return {"recommended": rec, "iv": iv, "iv_rank": round(iv_rank, 3),
            "reason": f"IV rank {iv_rank:.1%} suggests {'selling' if iv_rank > 0.5 else 'buying'} volatility"}
