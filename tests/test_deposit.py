from base import SqliteTestCase
from common.domain.entities import User
from common.domain.manager import Manager


class TestDeposit(SqliteTestCase):

    def setUp(self) -> None:
        super().setUp()

        self.user_id = 'user-1'
        self.amount = 100
        self.manager = Manager()

    def test_deposit_for_non_existing_user_success(self):
        self.manager.user_deposit(self.user_id, self.amount)
        user = self.manager.repository.get(User.create_id(self.user_id))

        self.assertEqual(user.balance, self.amount)

        event_types = [type(event) for event in self.manager.events.get(user.id)]
        self.assertListEqual(event_types, [User.Created, User.Deposited])

        self.manager.user_deposit(self.user_id, self.amount)
        user = self.manager.repository.get(user.id)

        self.assertEqual(user.balance, 2 * self.amount)
