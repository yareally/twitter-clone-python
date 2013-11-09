# coding=utf-8
import os
from redis import StrictRedis, WatchError
from models.user import User
import scrypt


class RedisBase(object):
    """
    Base helper class for redis communication
    """

    def __init__(self, redis_connection):
        self.redis = redis_connection


    @staticmethod
    def _set_key_string(primary_key, *secondary_keys):
        """
        Binds lookup keys to a string to query in redis.
        Examples:
        __set_key_string('user', 'id', email') returns 'user:id:email'
        __set_key_string('user', 'id') returns 'user:id'

        @param primary_key: required main key to look up or set a value in redis (ex: 'user')
        @type: str
        @param secondary_keys: required subkey to look up or set a value in redis (ex: 'id')
        @type: ()
        @return: The previous entry for the key being set or None if no previous entry exists
        @rtype: str
        """
        query = ':'.join((primary_key,) + secondary_keys)
        return query


class UserHelper(RedisBase):
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
    __QUERY_STRING = 'user'

    def __init__(self, redis_connection, user_id=None):
        super(UserHelper, self).__init__(redis_connection)
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
        username_key = self.__set_user_string(twit_user.username, User.USER_ID_KEY)
        email_key = self.__set_user_string(twit_user.email, User.USER_ID_KEY)

        # TODO: use MSET instead of SET
        with self.redis.pipeline() as trans:
            trans.set(username_key, twit_user.id)
            trans.set(email_key, twit_user.id)

            for key, value in twit_user.items():
                if value == twit_user.password:
                    value = UserHelper.hash_password(twit_user.password, twit_user.salt)
                trans.set(self.__set_user_string(twit_user.id, key), value)

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
        # TODO: use MGET instead of GET
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
        user_id = self.redis.get(self.__set_user_string(email, User.USER_ID_KEY))
        return self.get_user_by_id(user_id)


    def get_user_by_username(self, username):
        """

        @param username:
        @type username: str
        @return: The queried user object or None if not found
        @rtype: User
        """

        user_id = self.redis.get(self.__set_user_string(username, User.USER_ID_KEY))
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
            raise ValueError('At least one of these parameters: (%s, %s or %s) must not be empty'
                             % (User.USER_ID_KEY, User.EMAIL_KEY, User.USERNAME_KEY))
        user = User()

        if user_id:
            user = self.get_user_by_id(user_id)
        elif email:
            user = self.get_user_by_email(email)
        else:
            user = self.get_user_by_username(username)

        to_delete = map(lambda (k, v): (self.__set_user_string(user.id, k)), user.items())
        to_delete += (self.__set_user_string(user.username, User.USER_ID_KEY),
                      self.__set_user_string(user.email, User.USER_ID_KEY),
                      self.__set_user_string(user.id, User.FOLLOWING_ID_KEY),
                      self.__set_user_string(user.id, User.FOLLOWERS_ID_KEY))

        # TODO: remove the user from anyone that was following them as well
        with self.redis.pipeline() as trans:
            trans.delete(*to_delete)
            result = trans.execute()
        return result

    def add_follower(self, follower_id, user_id=None):
        """
        Adds a follower to a user.

        @param follower_id: The user id of the follower to add to this user
        @type follower_id: int
        @param user_id: The user id to add the follower to
        @type user_id: int
        """
        if not user_id:
            user_id = self.user_id
        self.redis.sadd(self.__set_user_string(user_id, User.FOLLOWERS_ID_KEY), follower_id)
        # Also add user to the following user's people they follow set
        self.redis.sadd(self.__set_user_string(follower_id, User.FOLLOWING_ID_KEY), user_id)


        #elif value is list():
        #    self.redis.lpush(self.__set_user_string(twit_user.id, key), value)
        #elif value is dict():
        #    self.redis.zadd(self.__set_user_string(twit_user.id, key), value)

    def get_follower_ids(self, user_id=None):
        """
        Fetches a set of all follower user ids for a user
        @param user_id: user whose follower ids should be queried
        @type user_id: int
        @return: set of all follower ids for the user
        @rtype: set
        """
        if not user_id:
            user_id = self.user_id
        return self.redis.smembers(self.__set_user_string(user_id, User.FOLLOWERS_ID_KEY))

    def add_following(self, follow_id, user_id=None):
        """
        Adds a user to follow to the current user

        @param follow_id: The user id of the person to follow
        @type follow_id: int
        @param user_id: The user id of the person wanting to follow someone
        @type user_id: int
        """
        if not user_id:
            user_id = self.user_id
        self.redis.sadd(self.__set_user_string(user_id, User.FOLLOWING_ID_KEY), follow_id)
        # Also add the follower since the user is now following this person
        self.redis.sadd(self.__set_user_string(follow_id, User.FOLLOWERS_ID_KEY), user_id)


    def get_post_id_range(self, start_post_id, end_post_id, user_id=None):
        """
        Gets the user post ids within a range
        @param user_id: user id to get post ids from
        @type user_id: int
        @return: list of all user posts within the start/end range
        @rtype: list
        """
        if not user_id:
            user_id = self.user_id
        return self.redis.lrange(self.__set_user_string(user_id, User.POSTS_ID_KEY), start_post_id, end_post_id)

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
        if password is not bytes:
            password = bytes(password)
        if salt is not bytes:
            salt = bytes(salt)
        return scrypt.hash(password, salt)

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
        @type first_key: str, int
        @param second_key:
        @type second_key: str
        @return: The previous entry for the key being set or None if no previous entry exists
        @rtype: str
        """

        if not first_key:
            first_key = self.user_id
        return self._set_key_string(self.__QUERY_STRING, str(first_key), second_key)

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