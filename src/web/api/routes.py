from fastapi import APIRouter

from common.domain.manager import Manager
from common.models.basic import StockData, UserData
from web.models.requests import TransactionRequest, OrderRequest
from web.models.responses import Content

router = APIRouter()

manager = Manager()


@router.get("/health", response_model=Content[None])
def health_check():
    return Content()


@router.post("/deposit", response_model=Content[None])
def deposit(request: TransactionRequest):
    manager.user_deposit(request.user_id, request.amount)
    return Content()


@router.post("/withdraw", response_model=Content[None])
def withdraw(request: TransactionRequest):
    manager.user_withdraw(request.user_id, request.amount)
    return Content()


@router.post("/buy", response_model=Content[None])
def buy(request: OrderRequest):
    manager.user_buy(request.user_id, request.stock_id, request.total, request.upper_bound, request.lower_bound)
    return Content()


@router.post("/sell", response_model=Content[None])
def sell(request: OrderRequest):
    manager.user_sell(request.user_id, request.stock_id, request.total, request.upper_bound, request.lower_bound)
    return Content()


@router.put("/stock", response_model=Content[None])
def update_stock(request: dict):
    manager.stock_update(request['stock_id'], request['name'], request['price'], request['availability'])
    return Content()


@router.get("/stock/{stock_id}", response_model=Content[StockData])
def get_stock(stock_id: str):
    stock = manager.get_stock(stock_id)
    return Content(details=StockData(id=stock.stock_id,
                                     name=stock.name,
                                     price=stock.price,
                                     availability=stock.availability))


@router.get("/user/{user_id}", response_model=Content[UserData])
def get_stock(user_id: str):
    user = manager.get_user(user_id)
    return Content(details=UserData(id=user.user_id,
                                    balance=user.balance,
                                    inventory=user.inventory))
