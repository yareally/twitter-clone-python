# coding=utf-8
import os
import scrypt
import time
from redis import StrictRedis
from redis_wrap import HashFu, ListFu, SetFu

class Token(object):

    """

    @param redis_connection:
    @type redis_connection: StrictRedis
    """

    def __init__(self, redis_connection):
        self.redis = redis_connection

        # get or create some password to encrypt the user verification token
        self.password = self.redis.get('token_pass')

        if not self.password:
            salt = os.urandom(16).encode('base_64')
            password = os.urandom(24).encode('base_64')
            self.redis.set('token_pass', scrypt.hash(password, salt))
            # TODO: should probably be the user passwords instead, but change that later
            self.password = self.redis.get('token_pass')

    def generate_token(self):
        """
        Generates an encrypted token for validating a user
        @return: the encrypted token (a random value and the date as a timestamp
        @rtype: str
        """
        # random value, timestamp
        values = '%s,%d' % (os.urandom(16).encode('base_64'), time.time())
        return scrypt.encrypt(values, self.password)

    def store_token(self, key):
        """
        Generates and stores the encrypted token in redis
        @param key:
        @param token:
        """
        token = self.generate_token()

        self.redis.set(key, token)
        return token

    def validate_token(self, lookup_key, client_token, expire_time=15):
        """

        @return:
        """
        tokens = scrypt.decrypt(client_token, self.password).split(',')
        server_token = self.redis.get(lookup_key)
       # if tokens[0] ==
