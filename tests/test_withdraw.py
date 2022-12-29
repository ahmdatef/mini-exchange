from eventsourcing.application import AggregateNotFound

from base import SqliteTestCase
from common.domain.entities import User
from common.domain.manager import Manager
from common.models.errors import BadRequest


class TestWithdraw(SqliteTestCase):

    def setUp(self) -> None:
        super().setUp()

        self.user_id = 'user-1'
        self.amount = 100
        self.manager = Manager()

    def test_withdraw_for_non_existing_user_fail(self):
        self.assertRaises(AggregateNotFound, self.manager.user_withdraw, self.user_id, self.amount)

    def test_withdraw_for_existing_user_success(self):
        self.manager.user_deposit(self.user_id, self.amount)
        self.manager.user_withdraw(self.user_id, self.amount)

        user = self.manager.repository.get(User.create_id(self.user_id))

        self.assertEqual(user.balance, 0)

    def test_withdraw_insufficient_funds_fail(self):
        self.manager.user_deposit(self.user_id, self.amount)
        self.manager.user_withdraw(self.user_id, self.amount)

        self.assertRaises(BadRequest, self.manager.user_withdraw, self.user_id, self.amount)
