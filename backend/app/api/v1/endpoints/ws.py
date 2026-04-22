from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from loguru import logger
import asyncio, json, time, random, math

router = APIRouter()

@router.websocket("/feed")
async def websocket_feed(ws: WebSocket):
    await ws.accept()
    spot = 65000.0; iv = 0.65
    logger.info("WS client connected")
    try:
        while True:
            spot *= math.exp(random.gauss(0, 0.001))
            spot = max(30000, min(150000, spot))
            iv = max(0.20, min(2.0, iv + random.gauss(0, 0.003)))
            await ws.send_json({
                "type": "ticker",
                "spot": round(spot, 2),
                "bid": round(spot - spot*0.0001, 2),
                "ask": round(spot + spot*0.0001, 2),
                "iv": round(iv, 4),
                "volume": round(random.uniform(800, 1200), 1),
                "timestamp": int(time.time()*1000)
            })
            await asyncio.sleep(0.5)
    except WebSocketDisconnect:
        logger.info("WS client disconnected")
    except Exception as e:
        logger.error(f"WS error: {e}")
