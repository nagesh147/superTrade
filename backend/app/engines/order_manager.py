"""
Order Management System (OMS)
Full lifecycle: create → validate → submit → track → fill → settle
Paper trading + live exchange support
"""
import uuid
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Dict
from loguru import logger


class OrderStatus(str, Enum):
    PENDING   = "pending"
    OPEN      = "open"
    PARTIALLY_FILLED = "partially_filled"
    FILLED    = "filled"
    CANCELLED = "cancelled"
    REJECTED  = "rejected"
    EXPIRED   = "expired"


class OrderType(str, Enum):
    MARKET = "market"
    LIMIT  = "limit"
    STOP   = "stop"
    STOP_LIMIT = "stop_limit"
    POST_ONLY  = "post_only"


class OrderSide(str, Enum):
    BUY  = "buy"
    SELL = "sell"


class TimeInForce(str, Enum):
    GTC = "gtc"   # Good Till Cancel
    IOC = "ioc"   # Immediate or Cancel
    FOK = "fok"   # Fill or Kill
    GTD = "gtd"   # Good Till Date


@dataclass
class Order:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    symbol: str = ""
    side: OrderSide = OrderSide.BUY
    order_type: OrderType = OrderType.LIMIT
    quantity: float = 0.0
    price: Optional[float] = None
    stop_price: Optional[float] = None
    time_in_force: TimeInForce = TimeInForce.GTC
    status: OrderStatus = OrderStatus.PENDING
    filled_qty: float = 0.0
    avg_fill_price: float = 0.0
    commission: float = 0.0
    created_at: int = field(default_factory=lambda: int(time.time()*1000))
    updated_at: int = field(default_factory=lambda: int(time.time()*1000))
    exchange_id: Optional[str] = None
    strategy_id: Optional[str] = None
    legs: List[str] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)

    @property
    def remaining_qty(self): return self.quantity - self.filled_qty
    @property
    def is_active(self): return self.status in [OrderStatus.OPEN, OrderStatus.PARTIALLY_FILLED]
    @property
    def fill_pct(self): return self.filled_qty / self.quantity * 100 if self.quantity else 0


@dataclass
class Fill:
    order_id: str; price: float; quantity: float
    commission: float; timestamp: int = field(default_factory=lambda: int(time.time()*1000))
    trade_id: str = field(default_factory=lambda: str(uuid.uuid4()))


class OrderManager:
    def __init__(self, paper_mode: bool = True, commission_rate: float = 0.0003):
        self.paper_mode = paper_mode
        self.commission_rate = commission_rate
        self.orders: Dict[str, Order] = {}
        self.fills: List[Fill] = []
        self.positions: Dict[str, float] = {}  # symbol -> net qty
        self.cash: float = 100_000.0
        logger.info(f"OMS initialized: paper={paper_mode}")

    def create_order(self, symbol: str, side: OrderSide, order_type: OrderType,
                     quantity: float, price: Optional[float] = None,
                     strategy_id: Optional[str] = None, **kwargs) -> Order:
        order = Order(
            symbol=symbol, side=side, order_type=order_type,
            quantity=quantity, price=price, strategy_id=strategy_id,
            status=OrderStatus.PENDING, **kwargs
        )
        self.orders[order.id] = order
        logger.info(f"Order created: {order.id} {side} {quantity} {symbol} @ {price}")
        return order

    def validate_order(self, order: Order, available_cash: float, spot: float) -> tuple:
        errors = []
        if order.quantity <= 0: errors.append("Quantity must be > 0")
        if order.order_type == OrderType.LIMIT and not order.price:
            errors.append("Limit order requires price")
        notional = order.quantity * (order.price or spot)
        if order.side == OrderSide.BUY and notional > available_cash:
            errors.append(f"Insufficient funds: need ${notional:.2f}, have ${available_cash:.2f}")
        return len(errors) == 0, errors

    async def submit_order(self, order: Order, spot_price: float) -> Order:
        valid, errors = self.validate_order(order, self.cash, spot_price)
        if not valid:
            order.status = OrderStatus.REJECTED
            order.metadata["reject_reason"] = "; ".join(errors)
            logger.warning(f"Order rejected: {errors}")
            return order

        order.status = OrderStatus.OPEN
        order.updated_at = int(time.time()*1000)

        if self.paper_mode:
            order = await self._paper_fill(order, spot_price)

        return order

    async def _paper_fill(self, order: Order, market_price: float) -> Order:
        """Simulate realistic fill with slippage"""
        if order.order_type == OrderType.MARKET:
            slippage = market_price * 0.0005 * (1 if order.side == OrderSide.BUY else -1)
            fill_price = market_price + slippage
        elif order.order_type == OrderType.LIMIT:
            if (order.side == OrderSide.BUY and market_price <= order.price) or \
               (order.side == OrderSide.SELL and market_price >= order.price):
                fill_price = order.price
            else:
                return order  # Not filled yet
        else:
            fill_price = market_price

        commission = order.quantity * fill_price * self.commission_rate
        fill = Fill(order_id=order.id, price=fill_price, quantity=order.quantity, commission=commission)
        self.fills.append(fill)

        order.filled_qty = order.quantity
        order.avg_fill_price = fill_price
        order.commission = commission
        order.status = OrderStatus.FILLED
        order.updated_at = int(time.time()*1000)

        # Update position and cash
        sign = 1 if order.side == OrderSide.BUY else -1
        self.positions[order.symbol] = self.positions.get(order.symbol, 0) + sign * order.quantity
        cost = sign * order.quantity * fill_price + commission
        self.cash -= cost

        logger.info(f"Fill: {order.id} {order.quantity} @ {fill_price:.2f} (fee: ${commission:.4f})")
        return order

    def cancel_order(self, order_id: str) -> Order:
        order = self.orders.get(order_id)
        if not order: raise ValueError(f"Order {order_id} not found")
        if not order.is_active: raise ValueError(f"Order {order_id} not cancellable: {order.status}")
        order.status = OrderStatus.CANCELLED
        order.updated_at = int(time.time()*1000)
        return order

    def get_position(self, symbol: str) -> float:
        return self.positions.get(symbol, 0.0)

    def get_all_orders(self, status: Optional[OrderStatus] = None) -> List[Order]:
        orders = list(self.orders.values())
        if status: orders = [o for o in orders if o.status == status]
        return sorted(orders, key=lambda o: o.created_at, reverse=True)

    def get_fills(self) -> List[Fill]: return sorted(self.fills, key=lambda f: f.timestamp, reverse=True)

    def portfolio_summary(self) -> dict:
        return {"cash": self.cash, "positions": dict(self.positions),
                "n_orders": len(self.orders), "n_fills": len(self.fills)}
