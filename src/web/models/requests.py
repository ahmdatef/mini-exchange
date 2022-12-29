from pydantic import BaseModel


class TransactionRequest(BaseModel):
    user_id: str
    amount: int


class OrderRequest(BaseModel):
    user_id: str
    stock_id: str
    total: int
    upper_bound: int
    lower_bound: int