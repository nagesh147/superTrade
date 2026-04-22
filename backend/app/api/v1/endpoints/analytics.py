from fastapi import APIRouter, Request
import random, math

router = APIRouter()

@router.get("/pnl-chart")
async def pnl_chart(request: Request, days: int = 30):
    data = []
    val = 100000.0
    for i in range(days):
        val *= (1 + random.gauss(0.002, 0.015))
        data.append({"day": i, "value": round(val, 2), "pnl": round(val - 100000, 2)})
    return {"data": data}

@router.get("/greeks-breakdown")
async def greeks_breakdown(request: Request):
    market = request.app.state.market
    spot = market.get_spot()
    return {
        "delta": round(random.gauss(0.05, 0.3), 4),
        "gamma": round(abs(random.gauss(0, 0.001)), 6),
        "theta": round(random.gauss(-50, 20), 2),
        "vega": round(random.gauss(200, 100), 2),
        "dollar_delta": round(spot * random.gauss(0.05, 0.3), 2),
    }
