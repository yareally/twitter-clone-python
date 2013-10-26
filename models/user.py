from collections import OrderedDict


class User(object):
    """

    @param username:
    @param email:
    @param password:
    @param name:
    """

    _values = dict
    messages = OrderedDict

    def __init__(self, username = '', email = '', password = '', name=''):
        self._values['username'] = username
        self._values['email'] = email
        self._values['name'] = name
        self._values['password'] = password
        self._values['id'] = 0


    @property
    def email(self):
        return self._values['email']

    @property
    def username(self):
        return self._values['username']

    @property
    def password(self):
        return self._values['password']

    @property
    def name(self):
        return self._values['name']

    @property
    def id(self):
        return self._values['id']

    @id.setter
    def id(self, value):
        self._values['id'] = value

    def __iter__(self):
        return self._values.__iter__()

    def __setitem__(self, key, value):
        self._values[key] = value

    def __getitem__(self, item):
        return self._values[item]