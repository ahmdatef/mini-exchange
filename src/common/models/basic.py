from datetime import datetime, timedelta

from pydantic import BaseModel, PrivateAttr


def _expiry_factory():
    from common.config.settings import get_settings
    settings = get_settings()

    return datetime.now() + timedelta(seconds=settings.order_expiry)


class Order(BaseModel):
    user_id: str
    total: int
    upper_bound: int
    lower_bound: int

    _expiry: datetime = PrivateAttr(default_factory=_expiry_factory)

    def is_expired(self) -> bool:
        return self._expiry < datetime.now()


class BuyOrder(Order):
    """
    Used for buyers
    """


class SellOrder(Order):
    """
    Used for sellers
    """


class StockData(BaseModel):
    id: str
    name: str
    price: int
    availability: int


class UserData(BaseModel):
    id: str
    balance: int
    inventory: dict