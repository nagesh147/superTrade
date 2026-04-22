from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.engines.order_manager import OrderSide, OrderType, TimeInForce

router = APIRouter()

class OrderRequest(BaseModel):
    symbol: str; side: str; order_type: str; quantity: float
    price: Optional[float] = None; strategy_id: Optional[str] = None
    time_in_force: str = "gtc"

@router.post("/create")
async def create_order(req: OrderRequest, request: Request):
    oms = request.app.state.oms
    market = request.app.state.market
    spot = market.get_spot()
    order = oms.create_order(
        symbol=req.symbol, side=OrderSide(req.side),
        order_type=OrderType(req.order_type), quantity=req.quantity,
        price=req.price, strategy_id=req.strategy_id
    )
    order = await oms.submit_order(order, spot)
    return {"order_id": order.id, "status": order.status, "fill_price": order.avg_fill_price}

@router.get("/")
async def list_orders(request: Request, status: Optional[str] = None):
    oms = request.app.state.oms
    from app.engines.order_manager import OrderStatus
    st = OrderStatus(status) if status else None
    orders = oms.get_all_orders(st)
    return {"orders": [{"id": o.id, "symbol": o.symbol, "side": o.side, "qty": o.quantity,
                        "price": o.price, "status": o.status, "filled": o.filled_qty,
                        "avg_price": o.avg_fill_price, "commission": o.commission} for o in orders[:50]]}

@router.delete("/{order_id}")
async def cancel_order(order_id: str, request: Request):
    try:
        order = request.app.state.oms.cancel_order(order_id)
        return {"status": "cancelled", "order_id": order.id}
    except ValueError as e:
        raise HTTPException(400, str(e))

@router.get("/fills")
async def get_fills(request: Request):
    fills = request.app.state.oms.get_fills()
    return {"fills": [{"trade_id": f.trade_id, "order_id": f.order_id,
                       "price": f.price, "qty": f.quantity, "commission": f.commission} for f in fills[:100]]}
