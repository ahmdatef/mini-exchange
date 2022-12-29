from uuid import uuid4

from base import SqliteTestCase
from common.domain.entities import User, Stock
from common.domain.manager import Manager
from common.models.basic import BuyOrder


class TestBuy(SqliteTestCase):

    def setUp(self) -> None:
        super().setUp()

        self.user_id = 'user-1'
        self.amount = 100
        self.manager = Manager()

        self.stock_id = str(uuid4())
        self.stock_name = 'cib'
        self.stock_availability = 30

    def test_buy_with_direct_success(self):
        stock_price = self.amount // 10
        self.manager.stock_update(self.stock_id, self.stock_name, stock_price, self.stock_availability)
        self.manager.user_deposit(self.user_id, self.amount)

        total = 3
        self.manager.user_buy(self.user_id, self.stock_id, total, stock_price + 10, stock_price - 10)

        user = self.manager.repository.get(User.create_id(self.user_id))

        self.assertEqual(user.balance, self.amount - total * stock_price)
        self.assertDictEqual(user.inventory, {self.stock_id: total})

    def test_buy_with_wrong_window_success(self):
        stock_price = self.amount // 10
        self.manager.stock_update(self.stock_id, self.stock_name, stock_price, self.stock_availability)
        self.manager.user_deposit(self.user_id, self.amount)

        total = 3
        upper_bound = stock_price - 1
        lower_bound = stock_price + 1
        self.manager.user_buy(self.user_id, self.stock_id, total, upper_bound, lower_bound)

        user = self.manager.repository.get(User.create_id(self.user_id))
        stock = self.manager.repository.get(Stock.create_id(self.stock_id))

        self.assertEqual(user.balance, self.amount)
        self.assertListEqual(stock.orders, [BuyOrder(user_id=self.user_id,
                                                     total=total,
                                                     upper_bound=upper_bound,
                                                     lower_bound=lower_bound)])

        self.assertDictEqual(user.inventory, {})

    def test_buy_with_wrong_total_success(self):
        stock_price = self.amount // 10
        self.manager.stock_update(self.stock_id, self.stock_name, stock_price, 0)
        self.manager.user_deposit(self.user_id, self.amount)

        total = 3
        upper_bound = stock_price + 10
        lower_bound = stock_price - 10
        self.manager.user_buy(self.user_id, self.stock_id, total, upper_bound, lower_bound)

        user = self.manager.repository.get(User.create_id(self.user_id))
        stock = self.manager.repository.get(Stock.create_id(self.stock_id))

        self.assertEqual(user.balance, self.amount)
        self.assertListEqual(stock.orders, [BuyOrder(user_id=self.user_id,
                                                     total=total,
                                                     upper_bound=upper_bound,
                                                     lower_bound=lower_bound)])

        self.assertDictEqual(user.inventory, {})

    def test_fulfilled_for_pending_buy_order_when_stock_updated(self):
        stock_price = self.amount // 10
        self.manager.stock_update(self.stock_id, self.stock_name, stock_price, 0)
        self.manager.user_deposit(self.user_id, self.amount)

        total = 3
        upper_bound = stock_price + 10
        lower_bound = stock_price - 10
        self.manager.user_buy(self.user_id, self.stock_id, total, upper_bound, lower_bound)

        user = self.manager.repository.get(User.create_id(self.user_id))
        stock = self.manager.repository.get(Stock.create_id(self.stock_id))

        self.assertEqual(user.balance, self.amount)
        self.assertListEqual(stock.orders, [BuyOrder(user_id=self.user_id,
                                                     total=total,
                                                     upper_bound=upper_bound,
                                                     lower_bound=lower_bound)])
        self.assertDictEqual(user.inventory, {})

        self.manager.stock_update(self.stock_id, self.stock_name, stock_price, self.stock_availability)

        user = self.manager.repository.get(User.create_id(self.user_id))
        stock = self.manager.repository.get(Stock.create_id(self.stock_id))

        self.assertEqual(user.balance, self.amount - total * stock_price)
        self.assertDictEqual(user.inventory, {self.stock_id: total})
        self.assertListEqual(stock.orders, [])

    def test_neglected_for_pending_buy_order_when_stock_updated_after_expiry(self):
        self.override_setting('order_expiry', 0)

        stock_price = self.amount // 10
        self.manager.stock_update(self.stock_id, self.stock_name, stock_price, 0)
        self.manager.user_deposit(self.user_id, self.amount)

        total = 3
        upper_bound = stock_price + 10
        lower_bound = stock_price - 10
        self.manager.user_buy(self.user_id, self.stock_id, total, upper_bound, lower_bound)

        user = self.manager.repository.get(User.create_id(self.user_id))
        stock = self.manager.repository.get(Stock.create_id(self.stock_id))

        self.assertEqual(user.balance, self.amount)
        self.assertListEqual(stock.orders, [BuyOrder(user_id=self.user_id,
                                                     total=total,
                                                     upper_bound=upper_bound,
                                                     lower_bound=lower_bound)])
        self.assertDictEqual(user.inventory, {})
        self.manager.stock_update(self.stock_id, self.stock_name, stock_price, self.stock_availability)

        user = self.manager.repository.get(User.create_id(self.user_id))
        stock = self.manager.repository.get(Stock.create_id(self.stock_id))

        self.assertEqual(user.balance, self.amount)
        self.assertListEqual(stock.orders, [])
        self.assertDictEqual(user.inventory, {})
        self.manager.stock_update(self.stock_id, self.stock_name, stock_price, self.stock_availability)
