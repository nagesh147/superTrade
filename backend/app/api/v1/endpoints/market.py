from fastapi import APIRouter, Request
from typing import Optional

router = APIRouter()

@router.get("/ticker")
async def get_ticker(request: Request):
    engine = request.app.state.market
    spot = engine.get_spot()
    iv = engine.get_iv()
    ticker = engine._cache.get("ticker")
    return {
        "spot": spot, "iv": iv,
        "bid": ticker.bid if ticker else spot - 10,
        "ask": ticker.ask if ticker else spot + 10,
        "volume_24h": ticker.volume_24h if ticker else 0,
        "open_interest": ticker.open_interest if ticker else 0,
    }

@router.get("/options-chain")
async def get_options_chain(request: Request, expiry: Optional[str] = None):
    engine = request.app.state.market
    spot = engine.get_spot()
    iv = engine.get_iv()
    chain = await engine.get_options_chain(spot, iv)
    data = []
    for e in chain:
        if expiry and e.expiry != expiry: continue
        data.append({
            "strike": e.strike, "expiry": e.expiry, "expiry_T": e.expiry_T,
            "call": {"bid": round(e.call_bid,2), "ask": round(e.call_ask,2),
                     "iv": round(e.call_iv,4), "delta": round(e.call_delta,4), "oi": round(e.call_oi)},
            "put":  {"bid": round(e.put_bid,2),  "ask": round(e.put_ask,2),
                     "iv": round(e.put_iv,4),  "delta": round(e.put_delta,4),  "oi": round(e.put_oi)},
        })
    return {"spot": spot, "iv_index": iv, "chain": data}

@router.get("/iv-surface")
async def get_iv_surface(request: Request):
    engine = request.app.state.market
    spot = engine.get_spot(); iv = engine.get_iv()
    chain = await engine.get_options_chain(spot, iv)
    surface = {}
    for e in chain:
        surface.setdefault(e.expiry, []).append({
            "strike": e.strike, "call_iv": e.call_iv, "put_iv": e.put_iv
        })
    return {"spot": spot, "surface": surface}
