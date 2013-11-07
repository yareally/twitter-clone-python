# coding=utf-8
import os
from redis import StrictRedis
from models.user import User
import scrypt


class UserHelper(object):
    """
    Handles user queries to redis

    @param redis_connection:
    @type redis_connection: StrictRedis
    @param user_id: if not empty, assumed the user exists already
    @type user_id: int
    """

    __NEXT_USER_KEY = 'next.user.id'

    # used to reference a key + value belonging to a specific user
    # order of the format is (user_id, user_attribute_key_name)
    # example: user:id:email = 'yarly@or.ly'
    __USER_ID_STRING_KEY = 'user:%s:%s'

    def __init__(self, redis_connection, user_id=None):
        self.redis = redis_connection
        # get the next unused id for the user to be inserted
        if not user_id:
            self.user_id = self.__next_user_id()
        else:
            self.user_id = user_id

    def add_user(self, twit_user):
        """

        @param twit_user:
        @type twit_user: User
        @return: the redis bound result after adding
        """
        twit_user.id = self.user_id
        trans = self.redis.pipeline()

        for key, value in twit_user.items():
            if value == twit_user.password:
                value = UserHelper.hash_password(twit_user.password)
            trans.set(self.__set_user_string(twit_user.id, key), value)

        trans.set(self.__set_user_string(twit_user.username, User.USER_ID_KEY), twit_user.id)
        email_key = self.__set_user_string(twit_user.email, User.USER_ID_KEY)
        trans.set(email_key, twit_user.id)

        result = trans.execute()
        return result

    # TODO: get user by email and get user by username

    def get_user_by_id(self, user_id=None):
        """

        @param user_id:
        @type user_id: int
        @return: or None if not found
        @rtype: User
        """

        if not user_id:
            user_id = self.user_id

        if not self.user_id_exists(user_id):
            return None

        user = User()

        for key, value in user.items():
            user[key] = self.redis.get(self.__set_user_string(str(user_id), key))

        return user

    def get_user_by_email(self, email):
        """

        @param email:
        @type email: str
        @return: the queried user object or None if not found
        @rtype: User
        """
        user_id = self.redis.get(self.__set_user_string(User.EMAIL_KEY, email))
        return self.get_user_by_id(user_id)


    def get_user_by_username(self, username):
        """

        @param username:
        @type username: str
        @return: The queried user object or None if not found
        @rtype: User
        """

        user_id = self.redis.get(self.__set_user_string(User.USERNAME_KEY, username))
        return self.get_user_by_id(user_id)

    def user_id_exists(self, user_id=None):
        """

        @param user_id:
        @type user_id: int
        @return: True if the user_id exists in the db
        @rtype: bool
        """
        if not user_id:
            user_id = self.user_id
        return self.redis.get(self.__set_user_string(str(user_id), User.USER_ID_KEY))

    def email_exists(self, email):
        """

        @param email:
        @type email: str
        @return: True if the email exists in the db
        @rtype: bool
        """
        result = self.__user_property_exists(email, User.USER_ID_KEY)
        return result

    def username_exists(self, username):
        """

        @param username:
        @type username: str
        @return: True if the username exists in the db
        @rtype: bool
        """
        return self.__user_property_exists(username, User.USER_ID_KEY)

    def delete_user(self, user_id='', email='', username=''):
        """

        @param user_id:
        @type user_id: int
        @param email:
        @type email: str
        @param username:
        @type username: str
        @return redis bound result from deletion
        @raise ValueError, ConnectionError: If something cannot be deleted or cannot connect to redis
        """
        if not user_id and not email and not username:
            raise ValueError('One of these parameters: user_id, email or username must not be empty')

        user = User()

        if user_id:
            user = self.get_user_by_id(user_id)
        elif email:
            user = self.get_user_by_email(email)
        else:
            user = self.get_user_by_username(username)

        to_delete = map(lambda (k,v): (self.__set_user_string(user.id, k)), user.items())
        to_delete += (self.__set_user_string(user.username, User.USER_ID_KEY),
                      self.__set_user_string(user.email, User.USER_ID_KEY))

        result = self.redis.delete(*to_delete)
        return result

    @staticmethod
    def hash_password(password, salt=''):
        """

        @param password: plaintext password to be hashed
        @type password: str
        @param salt: random characters to be added with the hashed password
        @type salt: str
        @return: the hashed password
        @rtype: str
        """
        if not salt:
            salt = UserHelper.generate_salt()
        return scrypt.hash(bytes(password), salt)

    @staticmethod
    def generate_salt(length=24):
        """

        @param length: Length of the salt
        @type length: int
        @return: the random salt string
        @rtype: int
        """
        salt = bytes(os.urandom(length).encode('base_64'))
        return salt

    def __user_property_exists(self, first_key, second_key):
        """

        @param first_key: Name of the stored key to check against in redis
        @type first_key: str
        @param second_key:
        @type second_key: str
        @rtype: bool
        """
        lookup_key = self.__set_user_string(first_key, second_key)
        result = self.redis.get(lookup_key)
        return result is not None

    def __set_user_string(self, first_key=None, second_key=''):
        """

        @param first_key:
        @type first_key: str
        @param second_key:
        @type second_key: str
        @return: The previous entry for the key being set or None if no previous entry exists
        @rtype: str
        """

        if not first_key:
            first_key = self.user_id
        return self.__USER_ID_STRING_KEY % (first_key, second_key)

    def __next_user_id(self):
        """
        Get the next user id from the db

        @rtype : int
        """
        return self.redis.incr(self.__NEXT_USER_KEY)

class MessageHelper(object):
    """
    Handles message queries to redis
    """

    _USER_MSG_STRING_KEY = 'user:%d:%s'