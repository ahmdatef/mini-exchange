from uuid import uuid4

from base import SqliteTestCase
from common.domain.entities import User, Stock
from common.domain.manager import Manager
from common.models.basic import BuyOrder, SellOrder
from common.models.errors import BadRequest


class TestSell(SqliteTestCase):

    def setUp(self) -> None:
        super().setUp()

        self.user_id = 'user-1'
        self.amount = 100
        self.manager = Manager()

        self.stock_id = str(uuid4())
        self.stock_name = 'cib'
        self.stock_availability = 30

        self.stock_price = self.amount // 10
        self.manager.stock_update(self.stock_id, self.stock_name, self.stock_price, self.stock_availability)
        self.manager.user_deposit(self.user_id, self.amount)

        self.total = 3
        upper_bound = self.stock_price + 10
        lower_bound = self.stock_price - 10
        self.manager.user_buy(self.user_id, self.stock_id, self.total, upper_bound, lower_bound)

        self.user = self.manager.repository.get(User.create_id(self.user_id))

        self.assertEqual(self.user.balance, self.amount - self.total * self.stock_price)
        self.assertDictEqual(self.user.inventory, {self.stock_id: self.total})

    def test_sell_with_direct_success(self):
        self.manager.user_sell(self.user_id, self.stock_id, self.total, self.stock_price + 10, self.stock_price - 10)

        user = self.manager.repository.get(User.create_id(self.user_id))

        self.assertEqual(user.balance, self.amount)
        self.assertDictEqual(user.inventory, {})

    def test_sell_with_wrong_window_success(self):
        wrong_upper_bound = self.stock_price - 10
        wrong_lower_bound = self.stock_price + 10
        self.manager.user_sell(self.user_id, self.stock_id, self.total, wrong_upper_bound, wrong_lower_bound)

        user = self.manager.repository.get(User.create_id(self.user_id))

        self.assertEqual(user.balance, self.amount - self.total * self.stock_price)
        self.assertDictEqual(user.inventory, {self.stock_id: self.total})

        stock = self.manager.repository.get(Stock.create_id(self.stock_id))

        self.assertListEqual(stock.orders, [SellOrder(user_id=self.user_id,
                                                      total=self.total,
                                                      upper_bound=wrong_upper_bound,
                                                      lower_bound=wrong_lower_bound)])

    def test_sell_with_wrong_total_success(self):
        upper_bound = self.stock_price + 10
        lower_bound = self.stock_price - 10

        self.assertRaises(BadRequest, self.manager.user_sell,
                          self.user_id, self.stock_id, self.total + 10, upper_bound, lower_bound)

    def test_fulfilled_for_pending_sell_order_when_stock_updated(self):
        self.manager.stock_update(self.stock_id, self.stock_name, self.stock_price + 1000, self.stock_availability)

        upper_bound = self.stock_price + 10
        lower_bound = self.stock_price - 10

        self.manager.user_sell(self.user_id, self.stock_id, self.total, upper_bound, lower_bound)

        user = self.manager.repository.get(User.create_id(self.user_id))
        stock = self.manager.repository.get(Stock.create_id(self.stock_id))

        self.assertDictEqual(user.inventory, {self.stock_id: self.total})
        self.assertListEqual(stock.orders, [SellOrder(user_id=self.user_id,
                                                      total=self.total,
                                                      upper_bound=upper_bound,
                                                      lower_bound=lower_bound)])

        self.manager.stock_update(self.stock_id, self.stock_name, self.stock_price, self.stock_availability)

        user = self.manager.repository.get(User.create_id(self.user_id))
        stock = self.manager.repository.get(Stock.create_id(self.stock_id))

        self.assertDictEqual(user.inventory, {})
        self.assertListEqual(stock.orders, [])

    def test_neglected_for_pending_sell_order_when_stock_updated_after_expiry(self):
        self.override_setting('order_expiry', 0)

        self.manager.stock_update(self.stock_id, self.stock_name, self.stock_price + 1000, self.stock_availability)

        upper_bound = self.stock_price + 10
        lower_bound = self.stock_price - 10

        self.manager.user_sell(self.user_id, self.stock_id, self.total, upper_bound, lower_bound)

        user = self.manager.repository.get(User.create_id(self.user_id))
        stock = self.manager.repository.get(Stock.create_id(self.stock_id))

        self.assertDictEqual(user.inventory, {self.stock_id: self.total})
        self.assertListEqual(stock.orders, [SellOrder(user_id=self.user_id,
                                                      total=self.total,
                                                      upper_bound=upper_bound,
                                                      lower_bound=lower_bound)])

        self.manager.stock_update(self.stock_id, self.stock_name, self.stock_price, self.stock_availability)

        user = self.manager.repository.get(User.create_id(self.user_id))
        stock = self.manager.repository.get(Stock.create_id(self.stock_id))

        self.assertDictEqual(user.inventory, {self.stock_id: self.total})
        self.assertListEqual(stock.orders, [])
