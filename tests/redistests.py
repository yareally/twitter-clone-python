# coding=utf-8
import unittest
import redis
from models.user import User
from libs import rediswrapper

class RedisTests(unittest.TestCase):
    """
    @param user: user instance to test
    @type user: User
    """
    user = User()

    def setUp(self):
        self.redis = redis.StrictRedis()
        self.dbh = rediswrapper.UserHelper(self.redis)
        self.user = User('a-user', 'email@whatever.com', 'plaintextemail', 'Jon Smith')

    def test_add_user(self):
        """
        Test adding a user to redis
        """
        self.dbh.add_user(self.user)
        self.assertTrue(self.dbh.email_exists(self.user.email))
        self.assertTrue(self.dbh.username_exists(self.user.username))
        self.assertTrue(self.dbh.user_id_exists(self.user.id))

    def get_user(self):
        """
        Test to see if a user can be retrieved from redis.
        """
        stored_user = self.dbh.get_user_by_id(self.user.id)
        self.assertEqual(self.user, stored_user)

    def tearDown(self):
        """
        Remove any data added to redis from tests and test that
        it was removed properly.
        @return:
        @rtype:
        """
        self.dbh.delete_user(self.user.id)
        self.assertFalse(self.dbh.user_id_exists(self.user.id))
        self.assertFalse(self.dbh.email_exists(self.user.email))
        self.assertFalse(self.dbh.username_exists(self.user.username))

if __name__ == '__main__':
    unittest.main()
