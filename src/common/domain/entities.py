from uuid import UUID, uuid5, NAMESPACE_URL

from eventsourcing.domain import Aggregate, event

from common.models.basic import Order


class Stock(Aggregate):
    @staticmethod
    def create_id(stock_id: str) -> UUID:
        return UUID(stock_id)

    @event('Created')
    def __init__(self, stock_id: str, name: str, price: int, availability: int) -> None:
        self.stock_id = stock_id
        self.name = name
        self.price = price
        self.availability = availability

        self.orders = []

    @event('Updated')
    def update(self, price: int, availability: int) -> None:
        self.price = price
        self.availability = availability

    @event('SubscriptionAdded')
    def subscribe(self, order: Order) -> None:
        self.orders.append(order)

    @event('SubscriptionRemoved')
    def unsubscribe(self, order: Order) -> None:
        self.orders.remove(order)


class User(Aggregate):
    @staticmethod
    def create_id(user_id: str) -> UUID:
        return uuid5(NAMESPACE_URL, f'/users/{user_id}')

    @event('Created')
    def __init__(self, user_id: str, balance: int = 0) -> None:
        self.user_id = user_id
        self.balance = balance

        self.inventory = {}

    @event('Deposited')
    def deposit(self, amount: int) -> None:
        self.balance += amount

    @event('Withdrew')
    def withdraw(self, amount: int) -> None:
        self.balance -= amount

    @event('Bought')
    def buy(self, stock_id: str, total: int, price: int) -> None:
        self.inventory[stock_id] = self.inventory.get(stock_id, 0) + total
        self.balance -= total * price

    @event('Sold')
    def sell(self, stock_id: str, total: int, price: int) -> None:
        self.inventory[stock_id] -= total
        if self.inventory[stock_id] == 0:
            del self.inventory[stock_id]
        self.balance += total * price
