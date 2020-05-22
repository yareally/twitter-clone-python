# coding=utf-8
import math
import os
from redis import StrictRedis, WatchError
import time
import uuid
from models.user import User
from models.message import Message
import scrypt

class RedisBase(object):
    """
    Base helper class for redis communication
    @type redis_connection: redis.client.StrictRedis
    """

    def __init__(self, redis_connection):
        self.redis = redis_connection


    @staticmethod
    def _set_key_string(primary_key, secondary_key):
        """
        Binds lookup keys to a string to query in redis.
        Examples:
        __set_key_string('user', 'id', email') returns 'user:id:email'
        __set_key_string('user', 'id') returns 'user:id'

        @param primary_key: required main key to look up or set a value in redis (ex: 'user')
        @type: str
        @param secondary_key: required subkey to look up or set a value in redis (ex: 'id')
        @type: str
        @return: The previous entry for the key being set or None if no previous entry exists
        @rtype: str
        """

        query =  '%s:%s' % (primary_key, secondary_key)
        return query

    def _lock_with_timeout(self, name, acquire_timeout=10, lock_timeout=10):
        """
        Sets a database lock with a timeout in case the user does not unlock it
        @param name: name for the lock
        @type name: str
        @param acquire_timeout: time in seconds to wait for the lock to be set or time out if not
        @type acquire_timeout: int
        @param lock_timeout: time in seconds to tell redis to hold the lock
        @type lock_timeout: int
        @return: the lock id if it's set or None if not
        @rtype: int
        """

        lock_id = str(uuid.uuid4())
        release_time = time.time() + acquire_timeout
        lock_timeout = int(math.ceil(lock_timeout))

        while time.time() < release_time:
            if self.redis.setnx(name, lock_id):
                self.redis.expire(name, lock_timeout)
                return lock_id
            elif not self.redis.ttl(name):
                self.redis.expire(name, lock_timeout)

            time.sleep(.001)
        return None

    def _release_lock(self, name, lock_id):
        """
        Releases a lock if it still exists
        @param name: name of the lock to release
        @type name: str
        @param lock_id: id of the lock to release
        @type lock_id: int
        @return: True if released, false if not
        @rtype: bool
        """
        with self.redis.pipeline() as trans:
            name = '%s:' % name

            while True:
                try:
                    trans.watch(name)

                    if trans.get(name) == lock_id:
                        trans.multi()
                        trans.delete(name)
                        trans.execute()
                        return True

                    trans.unwatch()
                    break
                except WatchError:
                    # someone was screwing with the lock, try again
                    pass
                    # lock was lost
        return False

    def _add_fuzzy_matches(self, key, value, trans):
        """
        Adds the value broken down into 1st letter, 1st + 2nd, 1st + 2nd + ...
        Should not be called directly, only used in another method adding a user
        @param key: Key to store/lookup the possible search fuzzy value
        @type key: str
        @param value: value to store as fuzzy matches
        @type value: str
        @param trans: the transaction the user is being added to currently
        @type trans: StrictPipeline
        @return: the transaction as it's not likely finished yet
        @rtype StrictPipeline
        """
        prefix = ''

        for char in value[0:-1]:
            prefix += char
            trans.zadd(key + ':search', 0, prefix)

        trans.zadd(key + ':search', 0, value + '*')
        return trans

    def _fuzzy_search_rank(self, key, prefix):
        """

        @param key:
        @type key: str
        @param prefix:
        @type prefix: str
        @return search results if there's a match or empty list if none
        @rtype list
        """
        results = []
        rangelen = 50
        count = 50
        start = self.redis.zrank(key + ':search', prefix)

        if not start:
            return []

        while len(results) != count:
            search_range = self.redis.zrange(key + ':search', start, start + rangelen - 1)
            start += rangelen

            if not search_range or len(search_range) == 0:
                break

            for entry in search_range:
                minlen = min([len(entry), len(prefix)])

                if entry[0:minlen - 1] != prefix[0:minlen - 1]:
                    count = len(results)
                    break

                if entry[-1] == '*' and len(results) != count:
                    results.append(entry[0:-1])
        return results


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
    _QUERY_STRING = 'user'

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
        @return: the user id of the inserted user or None if errors
        @rtype int
        """
        username_lock = self.__set_user_string(twit_user.username)
        email_lock = self.__set_user_string(twit_user.email)
        username_lock_id = self._lock_with_timeout(username_lock, 1)
        email_lock_id = self._lock_with_timeout(email_lock, 1)

        if not username_lock_id or self.username_exists(twit_user.username):
            return None

        twit_user.id = self.user_id

        redis = StrictRedis()
        redis.hset('hash-table-name', 'some-key', 'some-value')
        with self.redis.pipeline() as trans:
            trans.hset(self._QUERY_STRING, twit_user.username, twit_user.id)
            trans = self._add_fuzzy_matches(User.USERNAME_KEY, twit_user.username, trans)
            trans = self._add_fuzzy_matches(User.NAME_KEY, twit_user.name, trans)
            trans.hset(self._QUERY_STRING, twit_user.email, twit_user.id)
            trans.hmset(self.__set_user_string(twit_user.id), twit_user.get_dict())
            result = trans.execute()
            self._release_lock(username_lock, username_lock_id)
            self._release_lock(email_lock, email_lock_id)
        return twit_user.id if result else None

    def add_item(self, table, key, value):
        """
        Add a new item to the given hashtable.

        @param table: The name of the hash table.
        @type table: str
        @param key: The lookup key for the value
        @type key: str
        @param value: The value to store in the hashtable
        @type value: str
        @return: true if added
        @rtype: bool
        """
        # open a connection to redis
        redis = StrictRedis()
        # insert the key and value
        return redis.hset(table, key, value)

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
        user._values = self.redis.hgetall(self.__set_user_string(str(user_id)))
        user.msg_count = MessageHelper(self.redis).get_msg_count(user_id)
        return user

    def get_user_by_email(self, email):
        """

        @param email:
        @type email: str
        @return: the queried user object or None if not found
        @rtype: User
        """
        user_id = self.redis.hget(self._QUERY_STRING, email)
        return self.get_user_by_id(user_id)

    def get_all_usernames(self):
        """

        @return: dictionary of all users
        @rtype: dict
        """
        return self.redis.hgetall(self._QUERY_STRING)

    def fuzzy_username_search(self, prefix):
        """
        Does a search for partial usernames (first letter at least has to be correct)
        @param prefix: partial match
        @type prefix: str
        @return: possible matches
        @rtype: list
        """
        return self._fuzzy_search_rank(User.USERNAME_KEY, prefix)

    def get_user_by_username(self, username):
        """

        @param username:
        @type username: str
        @return: The queried user object or None if not found
        @rtype: User
        """

        user_id = self.redis.hget(self._QUERY_STRING, username)
        return self.get_user_by_id(user_id)

    def get_user_token(self, user_id=None):
        """
        If one exists, gets the temp user token used for web sockets and
        other sessionless means of communication

        @param user_id: the user id
        @type user_id: int
        @return: the token, if there is one (None otherwise)
        @rtype: str
        """
        if not user_id:
            user_id = self.user_id
        return self.redis.hget(self.__set_user_string())

    def user_id_exists(self, user_id=None):
        """

        @param user_id:
        @type user_id: int
        @return: True if the user_id exists in the db
        @rtype: bool
        """
        if not user_id:
            user_id = self.user_id
        return self.redis.exists(self.__set_user_string(user_id))

    def email_exists(self, email):
        """

        @param email:
        @type email: str
        @return: True if the email exists in the db
        @rtype: bool
        """
        result = self.redis.hget(self._QUERY_STRING, email)
        return result

    def username_exists(self, username):
        """

        @param username:
        @type username: str
        @return: True if the username exists in the db
        @rtype: bool
        """
        return self.redis.hget(self._QUERY_STRING, username)

    def delete_user(self, user_id='', email='', username=''):
        """

        @param user_id:
        @type user_id: int
        @param email:
        @type email: str
        @param username:
        @type username: str
        @return redis bound result from deletion
        @raise ValueError, ConnectionError: If no user params were defined or cannot connect to redis
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

        lock_name = self.__set_user_string('del:%s' % user.id)
        # TODO: ensure no actions are done on this user once it is in the process of being deleted
        lock_id = self._lock_with_timeout(lock_name, 30)

        if not lock_id:
            return None

        # TODO: remove the user from anyone that was following them as well
        with self.redis.pipeline() as trans:
            trans.hdel(self._QUERY_STRING, user.email, user.username)
            trans.delete(self.__set_user_string(user.id))
            result = trans.execute()
            self._release_lock(lock_name, lock_id)

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
        self.redis.sadd(self.__set_user_string(user_id), follower_id)
        # Also add user to the following user's people they follow set
        self.redis.sadd(self.__set_user_string(follower_id), user_id)


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
        return self.redis.smembers(self.__set_user_string(user_id))

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
        self.redis.sadd(self.__set_user_string(user_id), follow_id)
        # Also add the follower since the user is now following this person
        self.redis.sadd(self.__set_user_string(follow_id), user_id)


    def get_post_id_range(self, start_post_id, end_post_id, user_id=None):
        """
        Gets the user post ids within a range
        @param start_post_id:
        @param end_post_id:
        @param user_id: user id to get post ids from
        @type user_id: int
        @return: list of all user posts within the start/end range
        @rtype: list
        """
        if not user_id:
            user_id = self.user_id
        return self.redis.lrange(self.__set_user_string(user_id), start_post_id, end_post_id)

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

    def __user_property_exists(self, first_key):
        """

        @param first_key: Name of the stored key to check against in redis
        @type first_key: str
        @rtype: bool
        """
        lookup_key = self.__set_user_string(first_key)
        result = self.redis.get(lookup_key)
        return result is not None

    def __set_user_string(self, first_key=None):
        """

        @param first_key:
        @type first_key: str, int
        @return: The previous entry for the key being set or None if no previous entry exists
        @rtype: str
        """

        if not first_key:
            first_key = self.user_id
        return self._set_key_string(self._QUERY_STRING, str(first_key))

    def __next_user_id(self):
        """
        Get the next user id from the db

        @rtype : int
        """
        return self.redis.incr(self.__NEXT_USER_KEY)

class MessageHelper(RedisBase):
    """
    Handles message queries to redis
    @param redis_connection: The redis connection
    @type redis_connection: StrictRedis
    @param msg_id: id for the message
    @type msg_id: int
    """
    _QUERY_STRING = 'message'
    __NEXT_MSG_KEY = 'next.msg.id'

    def __init__(self, redis_connection, msg_id=None):
        super(MessageHelper, self).__init__(redis_connection)
        if not msg_id:
            self.msg_id = self.__next_msg_id()
        else:
            self.msg_id = msg_id


    def post_message(self, msg):
        """
        Creates a new message for a user
        @param msg: The message model object
        @type msg: Message
        @return: the result of adding the message
        """
        msg.id = self.msg_id

        with self.redis.pipeline() as trans:
            trans.rpush(self._set_key_string('%s:%s' % (UserHelper._QUERY_STRING, msg.user_id), User.POSTS_ID_KEY), msg.id)
            trans.hmset(self.__set_msg_string(msg.id), msg.get_dict())
            self.redis.sadd(self.__set_msg_string(msg.id, Message.RECIP_KEY), msg.recipients)
            self.redis.sadd(self.__set_msg_string(msg.id, Message.URL_KEY), msg.urls)
            self.redis.sadd(self.__set_msg_string(msg.id, Message.HT_KEY), msg.hashtags)
            self.redis.sadd(self.__set_msg_string(msg.id, Message.MSG_TOKENS_KEY), msg.tokens)
            #trans.hset(self.__set_msg_string(msg.id, Message.FAV_KEY), msg.favorited)
            #trans.hset(self.__set_msg_string(msg.id, Message.RT_KEY), msg.retweeted)
            #trans.hset(self.__set_msg_string(msg.id, Message.REPLY_KEY), msg.replies)
            #trans.hset(self.__set_msg_string(msg.id, Message.URL_KEY), msg.urls)
            #trans.hset(self.__set_msg_string(msg.id, Message.HT_KEY), msg.hashtags)
            # TODO: keep track of how many times a trend is used and whatever as its own hashtable
            result = trans.execute()
            self.msg_id = self.__next_msg_id() if result else self.msg_id
        return result

    def get_message(self, msg_id):
        """

        @param msg_id:
        @type msg_id: int
        @return:
        @rtype: Message
        """
        if not msg_id:
            msg_id = self.msg_id

        with self.redis.pipeline() as trans:
            message = Message(0, '')
            trans.hgetall(self.__set_msg_string(msg_id))
            message._values = trans.execute()[0]

        return message

    def get_user_messages(self, user_id, start_range=0, end_range=-1):
        """
        Returns the messages for a user within a range.

        Example: if start_range = 0, end_range = 9 then it returns the first 10
        messages ever posted by this user (remember it's len - 1 like arrays)

        @param user_id: id of the user to get messages
        @type user_id: int
        @param start_range: by default, gets the first message ever posted
        @type start_range: int
        @param end_range: by default, gets up to the last message ever posted
        @type end_range: int
        @return: all messages within the given range for a user
        @rtype: Message
        """

        msg_ids = self.redis.lrange(
            self._set_key_string('%s:%s' % (UserHelper._QUERY_STRING, user_id), User.POSTS_ID_KEY),
            start_range,
            end_range)

        messages = list()

        with self.redis.pipeline() as trans:
            for msg_id in msg_ids:
                trans.hgetall(self.__set_msg_string(msg_id))

            messages = trans.execute()

        msg_list = []

        for msg in messages:
            next_msg = Message(0, '')
            next_msg._values = msg
            msg_list.append(next_msg)
        return msg_list

    def get_msg_count(self, user_id):
        """
        Gets the total messages posted by a user

        @param user_id: the user's id
        @type user_id: int
        @return: the post count
        @rtype: int
        """
        return self.redis.llen(
            self._set_key_string('%s:%s' % (UserHelper._QUERY_STRING, user_id), User.POSTS_ID_KEY))

    def __set_msg_string(self, first_key=None, second_key=None):
        """

        @param first_key:
        @type first_key: str, int
        @return: The previous entry for the key being set or None if no previous entry exists
        @rtype: str
        """

        if not first_key:
            first_key = self.msg_id

        if second_key:
            first_key = '%s:%s' % (first_key, second_key)

        return self._set_key_string(self._QUERY_STRING, str(first_key))


    def __next_msg_id(self):
        """
        Get the next msg id from the db

        @rtype : int
        """
        return self.redis.incr(self.__NEXT_MSG_KEY)