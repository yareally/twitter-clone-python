# coding=utf-8
import unittest
import redis
from models.message import Message
from models.user import User
from libs.rediswrapper import UserHelper, MessageHelper


class RedisTests(unittest.TestCase):
    """
    @param user: user instance to test
    @type user: User
    """

    redis = redis.StrictRedis()
    dbh = UserHelper(redis)
    dbhm = MessageHelper(redis)
    user = User('a-user', 'email@whatever.com', 'plain-text-pass', 'Jon Smith')
    def setUp(self):
        pass

    def test_add_user(self):
        """
        Test adding a user to redis
        """

        if self.dbh.username_exists(self.user.username):
            self.user = self.dbh.get_user_by_username(self.user.username)
        else:
            user_id = self.dbh.add_user(self.user)
            self.user.id = user_id

        self.assertTrue(self.dbh.email_exists(self.user.email))
        self.assertTrue(self.dbh.username_exists(self.user.username))
        self.assertTrue(self.dbh.user_id_exists(self.user.id))

        stored_user = self.dbh.get_user_by_id(self.user.id)
        self.assertEqual(self.user.email, stored_user.email)
        self.assertEqual(self.user.username, stored_user.username)
        self.assertEqual(str(self.user.id), str(stored_user.id))
        self.assertEqual(self.user.salt, stored_user.salt)
        self.assertEqual(self.user.name, stored_user.name)
      #  self.assertEqual(self.user.followers, stored_self.user.followers)
       # self.assertEqual(self.user.following, stored_self.user.following)
      #  self.assertEqual(self.user.messages, stored_self.user.messages)

       # passwd = UserHelper.hash_password(self.user.password, stored_self.user.salt)
        self.assertEqual(self.user.password, stored_user.password)

    def test_add_message(self):
        if self.dbh.username_exists(self.user.username):
            self.user = self.dbh.get_user_by_username(self.user.username)
        else:
            user_id = self.dbh.add_user(self.user)
            self.user.id = user_id

        message = Message(self.user.id, 'Test twitter clone message number 1, yay!!!!')

        result = self.dbhm.post_message(message)
        self.assertTrue(result)
        stored_message = self.dbhm.get_message(message.id)
        self.assertEqual(stored_message.message, message.message)
        self.assertEqual(stored_message.user_id, str(message.user_id))

        message = Message(self.user.id, 'Another test message wooo')

        result = self.dbhm.post_message(message)
        self.assertTrue(result)
        stored_message = self.dbhm.get_message(message.id)
        self.assertEqual(stored_message.message, message.message)
        self.assertEqual(stored_message.user_id, str(message.user_id))

        messages = self.dbhm.get_user_messages(self.user.id)
        self.assertEqual(2, len(messages))

    #def test_add_follower(self):
    #    """
    #    Test adding and getting a follower
    #    """
    #    self.dbh.add_user(user)
    #    self.dbh.add_follower(2, self.user.id)
    #    followers = self.dbh.get_follower_ids(self.user.id)
    #    self.assertTrue('2' in followers)

    def tearDown(self):
        """
        Remove any data added to redis from tests and test that
        it was removed properly.
        @return:
        @rtype:
        """
        #if self.dbh.user_id_exists(self.user.id):
        #    self.dbh.delete_user(self.user.id)
        #
        #self.assertFalse(self.dbh.user_id_exists(self.user.id))
        #self.assertFalse(self.dbh.email_exists(self.user.email))
        #self.assertFalse(self.dbh.username_exists(self.user.username))

if __name__ == '__main__':
    unittest.main()
