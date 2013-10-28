# coding=utf-8
import os
import scrypt
import time
#from redis import StrictRedis
#from redis_wrap import HashFu, ListFu, SetFu

class Token(object):

    """

    @param redis_connection:
    @type redis_connection: StrictRedis
    """

    def __init__(self, password):
        #self.redis = redis_connection

        # get or create some password to encrypt the user verification token
        self.password = password #if password else self.redis.get('token_pass')
        #
        #if not self.password:
        #    salt = os.urandom(16).encode('base_64')
        #    password = os.urandom(24).encode('base_64')
        #    self.redis.set('token_pass', scrypt.hash(password, salt))
        #    self.password = self.redis.get('token_pass')

    def generate_token(self):
        """
        Generates an encrypted token for validating a user
        @return: the encrypted token (a random value and the date as a timestamp
        @rtype: str
        """
        # random value, timestamp
        values = '%s,%s' % (os.urandom(16).encode('base_64'), time.time())
        return scrypt.encrypt(values, self.password)

    def store_token(self, key):
        """
        Generates and stores the encrypted token in redis
        @param key:
        @param token:
        """
        token = self.generate_token()

       # self.redis.set(key, token)
        return token

    def validate_token(self, client_token, server_token, expire_time=15):

        """
        @param client_token:
        @type client_token: str
        @param server_token:
        @type server_token: str
        @param expire_time:
        @type expire_time: int
        @return: True if still valid
        @rtype: bool
        """
        tokens = scrypt.decrypt(client_token, self.password).split(',')
        expired = ((time.time() - int(tokens[1])) / 3600) >= expire_time

        if expired:
            return False

        if tokens[0] != server_token:
            return False

        return True
