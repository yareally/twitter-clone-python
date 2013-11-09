# coding=utf-8

import os


class User(object):
    """

    @param username:
    @param email:
    @param password:
    @param name:
    """

    USER_ID_KEY = 'id'
    USERNAME_KEY = 'username'
    EMAIL_KEY = 'email'
    PASS_KEY = 'password'
    NAME_KEY = 'name'
    SALT_KEY = 'salt'
    FOLLOWERS_ID_KEY = 'followers'
    FOLLOWING_ID_KEY = 'following'
    POSTS_ID_KEY = 'posts'

    def __init__(self, username='', email='', password='', name='', salt=''):
        self._values = dict()

        self._values[self.USERNAME_KEY] = username
        self._values[self.EMAIL_KEY] = email
        self._values[self.NAME_KEY] = name
        self._values[self.PASS_KEY] = bytes(password)
        self._values[self.SALT_KEY] = salt if salt else bytes(os.urandom(24).encode('base_64'))
        self._values[self.USER_ID_KEY] = 0

        self.followers = set()
        self.following = set()
        self.messages = list()
        # self.token = Token()

    @property
    def email(self):
        return self._values[self.EMAIL_KEY]

    @property
    def username(self):
        return self._values[self.USERNAME_KEY]

    @property
    def password(self):
        return str(self._values[self.PASS_KEY])

    @property
    def salt(self):
        return self._values[self.SALT_KEY]

    @property
    def name(self):
        return self._values[self.NAME_KEY]

    @property
    def id(self):
        return self._values[self.USER_ID_KEY]

    @id.setter
    def id(self, value):
        """
        @param value: The id for the user
        @type value: int
        """
        self._values[self.USER_ID_KEY] = value

    def items(self):
        """
        @return: dictionary of all properties for the user
        @rtype: dict
        """
        return self._values.items()

    def __iter__(self):
        return self._values.__iter__()

    def __setitem__(self, key, value):
        self._values[key] = value

    def __getitem__(self, item):
        return self._values[item]