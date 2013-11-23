import math
import time
from datetime import date, timedelta, datetime

# deal with < Python 3.3 where cPickle was not merged
from libs.parser import Parser

try:
    import cPickle as pickle
except ImportError:
    import pickle

class Message(object):
    """
    Model to store a message created by a user and relevant content

    @param user_id: who posted the message
    @type user_id:
    @param message: the actual raw message
    @type message: str
    @param recipients: who is the message to be sent to? (zero or more people)
    @type recipients: set
    @param hashtags: any hashtags for the message
    @type hashtags: set
    @param replies: users that replied to the message
    @type replies: list
    @param favorited: users that favorited the message
    @type favorited: set
    @param retweeted: users that retweeted the message
    @type retweeted: set
    """

    MSG_ID_KEY = 'id'
    USER_ID_KEY = 'user_id'
    MSG_KEY = 'message'
    POST_KEY = 'posted'
    FAV_KEY = 'favorite_by'
    RT_KEY = 'retweet_by'
    REPLY_KEY = 'replies'
    HT_KEY = 'hashtags'
    RECIP_KEY = 'recipients'
    URL_KEY = 'urls'
    MSG_TOKENS = 'tokens'

    def __init__(self, user_id, message, recipients=set(), urls=list(), hashtags=list(), replies=list(),
                 favorited=set(), retweeted=set()):
        self._values = dict()
        self._values[self.MSG_ID_KEY] = None
        self._values[self.USER_ID_KEY] = user_id
        self.recipients = recipients
        self.hashtags = hashtags
        self.urls = urls

        if not urls and not hashtags and not recipients:
            parsr = Parser(message)
            self.urls = parsr.urls
            self.hashtags = parsr.hashtags
            self.recipients = parsr.recipients
            self.tokens = parsr._msg_values

        self._values[self.MSG_KEY] = message
        self._values[self.POST_KEY] = int(math.ceil(time.time()))

        self.replies = replies
        self.favorited = favorited
        self.retweeted = retweeted


    @property
    def id(self):
        """
        The id for the message
        @return: the id
        @rtype: int
        """
        return self._values[self.MSG_ID_KEY]

    @id.setter
    def id(self, value):
        """
        @param value: The id for the message
        @type value: int
        """
        self._values[self.MSG_ID_KEY] = value

    @property
    def user_id(self):
        return self._values[self.USER_ID_KEY]

    @property
    def message(self):
        return self._values[self.MSG_KEY]

    @property
    def posted_time(self):
        """
        When was the message posted?
        @return: time it was posted in seconds (unix timestamp)
        @rtype: int
        """
        return self._values[self.POST_KEY]

    @property
    def formatted_time(self):
        """
        Returns something like "17 Nov 12" or "1h 20m" or "2m"
        @return: A string formatted to display to a user
        @rtype: str
        """
        posted_seconds = timedelta(seconds=int(self.posted_time - time.time()))
        time_posted = datetime(1, 1, 1) + posted_seconds

        # note that day and year add one more than they should (thus we do > 1 and not > 0)
        if time_posted.year > 1:
            return datetime.strftime(date.fromtimestamp(self.posted_time), '%-d %b %y')
        if time_posted.day > 1:
            return datetime.strftime(date.fromtimestamp(self.posted_time), '%-d %b')
        if time_posted.hour > 0:
            return '%dh %dm' % (time_posted.hour, time_posted.minute)
        return '%dm' % time_posted.minute

    def items(self):
        """
        @return: dictionary of all properties for the user
        @rtype: dict
        """
        return self._values.items()

    def get_dict(self):
        return self._values

    @staticmethod
    def load_message(pickled_msg):
        """
        Restores a user from the pickled archive to a Message object

        @param pickled_msg: the stored message as a pickle serialized string
        @type pickled_msg: str
        @return: the restored message object
        @rtype: Message
        """
        return pickle.loads(pickled_msg)

    def __iter__(self):
        return self._values.__iter__()

    def __setitem__(self, key, value):
        self._values[key] = value

    def __getitem__(self, item):
        return self._values[item]

    def __str__(self):
        """
        Converts the current message instance into a pickle serialized string
        @return: the serialized message
        @rtype: str
        """
        return pickle.dumps(self)

