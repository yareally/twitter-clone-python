# coding=utf-8
__author__ = 'wes'
import os

# deal with < Python 3.3 where cPickle was not merged
try:
    import cPickle as pickle
except ImportError:
    import pickle

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
    USER_HOME_URL = 'dash/%s'
    TOKEN_KEY = 'token'

    def __init__(self, username='', email='', password='', name='', salt='', msg_count=''):
        # import here to avoid circular dependency conflicts
        from libs.rediswrapper import UserHelper
        self._values = dict()

        self._values[self.USERNAME_KEY] = username.lower()
        self._values[self.EMAIL_KEY] = email
        self._values[self.NAME_KEY] = name
        self._values[self.SALT_KEY] = salt if salt else bytes(os.urandom(24).encode('base_64'))
        # if we already have a salt, then we can assume this user already exists
        # if the user doesn't exist, we can hash the password since it's in plaintext right now
        self._values[self.PASS_KEY] = bytes(password) if salt else UserHelper.hash_password(password,
                                                                                            self._values[
                                                                                                self.SALT_KEY])
        self._values[self.USER_ID_KEY] = 0
        #self._values[self.TOKEN_KEY] =
        self.followers = set()
        self.following = set()
        self.messages = list()
        self.msg_count = msg_count
        # self.token = Token()

    @property
    def email(self):
        """


        @return: @rtype:
        """
        return self._values[self.EMAIL_KEY]

    @property
    def username(self):
        """


        @return: @rtype:
        """
        return self._values[self.USERNAME_KEY]

    @property
    def password(self):
        """


        @return: @rtype:
        """
        return str(self._values[self.PASS_KEY])

    @property
    def salt(self):
        """


        @return: @rtype:
        """
        return self._values[self.SALT_KEY]

    @property
    def name(self):
        """


        @return: @rtype:
        """
        return self._values[self.NAME_KEY]

    @property
    def id(self):
        """


        @return: @rtype:
        """
        return self._values[self.USER_ID_KEY]

    @id.setter
    def id(self, value):
        """
        @param value: The id for the user
        @type value: int
        """
        self._values[self.USER_ID_KEY] = value

    @property
    def follower_count(self):
        """


        @return: @rtype:
        """
        return len(self.followers)

    @property
    def following_count(self):
        """


        @return: @rtype:
        """
        return len(self.following)

    def items(self):
        """
        @return: dictionary of all properties for the user
        @rtype: dict
        """
        return self._values.items()


    def get_dict(self):
        """


        @return: @rtype:
        """
        return self._values

    @staticmethod
    def load_user(pickled_user):
        """
        Restores a user from the pickled archive to a User object

        @param pickled_user: the stored user as a pickle serialized string
        @type pickled_user: str
        @return: the restored user object
        @rtype: User
        """
        return pickle.loads(pickled_user)

    def __iter__(self):
        return self._values.__iter__()

    def __setitem__(self, key, value):
        self._values[key] = value

    def __getitem__(self, item):
        return self._values[item]

    def __str__(self):
        """
        Converts the current user instance into a pickle serialized string
        @return: the serialized user
        @rtype: str
        """
        return pickle.dumps(self)
