# coding=utf-8
from collections import OrderedDict
from libs.rediswrapper import UserHelper
from libs.token import Token


class User(object):
    """

    @param username:
    @param email:
    @param password:
    @param name:
    """

    _values = dict()
    messages = OrderedDict()

    USER_ID_KEY = 'id'
    USERNAME_KEY = 'username'
    EMAIL_KEY = 'email'
    PASS_KEY = 'password'
    NAME_KEY = 'name'
    SALT     = 'salt'

    def __init__(self, username = '', email = '', password = '', name='', salt=''):
        self._values[self.USERNAME_KEY] = username
        self._values[self.EMAIL_KEY] = email
        self._values[self.NAME_KEY] = name
        self._values[self.PASS_KEY] = password
        self._values[self.SALT] = salt if salt else UserHelper.generate_salt()
        self._values[self.USER_ID_KEY] = 0
       # self.token = Token()

    @property
    def email(self):
        return self._values[self.EMAIL_KEY]

    @property
    def username(self):
        return self._values[self.USERNAME_KEY]

    @property
    def password(self):
        return self._values[self.PASS_KEY]

    @property
    def name(self):
        return self._values[self.NAME_KEY]

    @property
    def id(self):
        return self._values[self.USER_ID_KEY]

    @id.setter
    def id(self, value):
        self._values[self.USER_ID_KEY] = value

    def items(self):
        return self._values.items()

    def __iter__(self):
        return self._values.__iter__()

    def __setitem__(self, key, value):
        self._values[key] = value

    def __getitem__(self, item):
        return self._values[item]