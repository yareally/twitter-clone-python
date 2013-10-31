# coding=utf-8
from operator import xor
import os
import scrypt
import time

try:
    xrange
except NameError:
    xrange = range

class Token(object):
    """

    @param user_id:
    @type user_id:
    @param password:
    @type password:
    """

    __BLOCK_SIZE = 256
    __TRANS_5C = "".join(chr(x ^ 0x5c) for x in xrange(256))
    __TRANS_36 = "".join(chr(x ^ 0x36) for x in xrange(256))
    __I_SALT = os.urandom(16).encode('base_64')
    __O_SALT = os.urandom(16).encode('base_64')

    def __init__(self, user_id, password = None):

        self.user_id = user_id
        # get or create some password to encrypt the user verification token
        self.password = password #if password else self.redis.get('token_pass')

        if not self.password:
            salt = os.urandom(16).encode('base_64')
            self.password = scrypt.hash(os.urandom(24).encode('base_64'), salt)


    def generate_token(self):
        """
        Generates an encrypted token for validating a user
        @return: the encrypted token (a random value and the date as a timestamp
        @rtype: str
        """
        # random value, user_id, timestamp
        values = '%s,%s,%s' % (os.urandom(16).encode('base_64'), self.user_id, time.time())
        return scrypt.encrypt(values, self.password)

    def generate_hmac(self, key, message):
        """

        @param key: The user's generated password
        @type key: str
        @param message: message to hash for client-server authentication
        @type message: str
        @return: the hash based message auth code (to verify against the client sent one)
        @rtype: str
        """

        if len(key) > self.__BLOCK_SIZE:
            salt = os.urandom(16).encode('base_64')
            key = scrypt.hash(key, salt)

        key +=  chr(0) * (self.__BLOCK_SIZE - len(key))
        o_key_pad = xor(self.__TRANS_5C, key)
        i_key_pad = xor(self.__TRANS_36, key)

        return scrypt.hash(o_key_pad + scrypt.hash(i_key_pad + message, self.__I_SALT), self.__O_SALT)

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

        if client_token != server_token:
            return False

        tokens = scrypt.decrypt(client_token, self.password).split(',')

        if len(tokens) != 3:
            return False

        expired = ((time.time() - int(tokens[1])) / 3600) >= expire_time

        if expired:
            return False

        return True
