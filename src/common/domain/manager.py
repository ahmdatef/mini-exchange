import logging
from abc import ABC
from typing import Optional

from eventsourcing.application import Application, AggregateNotFound
from eventsourcing.persistence import Transcoder
from eventsourcing.utils import EnvType

from common.domain.entities import User, Stock
from common.models.errors import BadRequest
from common.models.basic import BuyOrder, SellOrder
from common.serializers.transcodings import BuyOrderTranscoding, SellOrderTranscoding


class BaseApplication(Application, ABC):
    def register_transcodings(self, transcoder: Transcoder) -> None:
        super().register_transcodings(transcoder)
        transcoder.register(BuyOrderTranscoding())
        transcoder.register(SellOrderTranscoding())

    def __init__(self, env: Optional[EnvType] = None) -> None:
        super().__init__(env)
        self.logger = logging.getLogger(self.name)


class Manager(BaseApplication):
    def stock_update(self, stock_id: str, name: str, price: int, availability: int) -> None:
        self.logger.info(f'updating stock {stock_id} ...')
        try:
            stock = self.repository.get(Stock.create_id(stock_id))
            stock.update(price, availability)
        except AggregateNotFound:
            stock = Stock(stock_id, name, price, availability)

        for order in stock.orders:
            if order.is_expired():
                stock.unsubscribe(order)
            elif order.lower_bound <= stock.price <= order.upper_bound:
                user = self.repository.get(User.create_id(order.user_id))
                stock.unsubscribe(order)
                if isinstance(order, BuyOrder) and stock.availability >= order.total:
                    user.buy(stock_id, order.total, stock.price)
                else:
                    user.sell(stock_id, order.total, stock.price)
                self.save(user)

        self.save(stock)

    def user_deposit(self, user_id: str, amount: int) -> None:
        self.logger.info(f'user {user_id} depositing ...')
        try:
            user = self.repository.get(User.create_id(user_id))
            user.deposit(amount)
            self.save(user)
        except AggregateNotFound:
            user = User(user_id)
            user.deposit(amount)
            self.save(user)

    def user_withdraw(self, user_id: str, amount: int) -> None:
        self.logger.info(f'user {user_id} withdrawing ...')
        user = self.repository.get(User.create_id(user_id))
        if user.balance < amount:
            raise BadRequest("Insufficient balance")

        user.withdraw(amount)
        self.save(user)

    def user_buy(self, user_id: str, stock_id: str, total: int, upper_bound: int, lower_bound: int) -> None:
        """
        Assumptions:
        - `total` is the number of available shares required to buy
        - `stock.availability` is only being updated by the data stream
        :param user_id:
        :param stock_id:
        :param total:
        :param upper_bound:
        :param lower_bound:
        :return:
        """
        self.logger.info(f'user {user_id} buying ...')
        user = self.repository.get(User.create_id(user_id))
        stock = self.repository.get(Stock.create_id(stock_id))

        if user.balance < total * stock.price:
            raise BadRequest("Insufficient balance")

        if lower_bound <= stock.price <= upper_bound and stock.availability >= total:
            user.buy(stock_id, total, stock.price)
            self.save(user)
        else:
            subscription = BuyOrder(user_id=user_id,
                                    total=total,
                                    upper_bound=upper_bound,
                                    lower_bound=lower_bound)
            stock.subscribe(subscription)
            self.save(stock)

    def user_sell(self, user_id: str, stock_id: str, total: int, upper_bound: int, lower_bound: int) -> None:
        """
        Assumptions:
        - `total` is the number of available shares required to sell
        - `stock.availability` is only being updated by the data stream
        :param user_id:
        :param stock_id:
        :param total:
        :param upper_bound:
        :param lower_bound:
        :return:
        """
        self.logger.info(f'user {user_id} selling ...')
        user = self.repository.get(User.create_id(user_id))
        stock = self.repository.get(Stock.create_id(stock_id))

        if user.inventory[stock_id] < total:
            raise BadRequest("Insufficient stock in inventory")

        if lower_bound <= stock.price <= upper_bound:
            user.sell(stock_id, total, stock.price)
            self.save(user)
        else:
            subscription = SellOrder(user_id=user_id,
                                     total=total,
                                     upper_bound=upper_bound,
                                     lower_bound=lower_bound)
            stock.subscribe(subscription)
            self.save(stock)

    def get_stock(self, stock_id: str) -> Stock:
        return self.repository.get(Stock.create_id(stock_id))

    def get_user(self, user_id: str) -> User:
        return self.repository.get(User.create_id(user_id))
