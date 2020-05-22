# coding=utf-8
__author__ = 'wes'
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
    MSG_TOKENS_KEY = 'tokens'
    # message with the tokens removed and placeholders inserted
    PARSED_MSG_KEY = 'parsed_msg'
    FMT_MSG_KEY = 'fmt_msg'

    def __init__(self, user_id, message, posted_time=0, recipients=set(), urls=set(), hashtags=set(), replies=set(), favorited=set(), retweeted=set()):
        self._values = dict()
        # holds sets, dicts, etc
        self._cplx_values = dict()
        self._values[self.MSG_ID_KEY] = None
        self._values[self.USER_ID_KEY] = user_id

        if not urls and not hashtags and not recipients:
            parsr = Parser(message)

            self._cplx_values[self.URL_KEY] = parsr.urls
            self._cplx_values[self.FMT_MSG_KEY] = parsr.formatted_msg
            self._cplx_values[self.HT_KEY] = parsr.hashtags
            self._cplx_values[self.RECIP_KEY] = parsr.recipients
            self._cplx_values[self.MSG_TOKENS_KEY] = parsr._msg_values
            self._cplx_values[self.PARSED_MSG_KEY] = parsr._parsed_message
        else:
            # formtted_url = set()
            # formatted_hts = set()
            # formatted_recip = set()
            #
            # for url in urls:
            #     formtted_url += self.__URL_HTML % url
            # urls = formtted_url
            #
            # for ht in hashtags:
            #     formatted_hts += self.__HT_HTML % ht
            # hashtags = formatted_hts
            #
            # for user in recipients:
            #     formatted_recip += self.__USER_HTML % user
            # recipients = formatted_recip
            self._cplx_values[self.URL_KEY] = urls
            self._cplx_values[self.HT_KEY] = hashtags
            self._cplx_values[self.RECIP_KEY] = recipients

        self._values[self.POST_KEY] = int(math.ceil(time.time()))

        self._values[self.MSG_KEY] = message

        self._cplx_values[self.REPLY_KEY] = replies
        self._cplx_values[self.FAV_KEY] = favorited
        self._cplx_values[self.RT_KEY] = retweeted


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
        """


        @return: @rtype:
        """
        return self._values[self.USER_ID_KEY]

    @property
    def message(self):
        """


        @return: @rtype:
        """
        return self._values[self.MSG_KEY]

    @property
    def formatted_msg(self):
        """


        @return: @rtype:
        """
        return self._cplx_values[self.FMT_MSG_KEY]

    @property
    def hashtags(self):
        """


        @return: @rtype:
        """
        return self._cplx_values[self.HT_KEY]

    @property
    def urls(self):
        """


        @return: @rtype:
        """
        return self._cplx_values[self.URL_KEY]

    @property
    def recipients(self):
        """


        @return: @rtype:
        """
        return self._cplx_values[self.RECIP_KEY]

    @property
    def tokens(self):
        """


        @return: @rtype:
        """
        return self._cplx_values[self.MSG_TOKENS_KEY]

    @property
    def parsed_msg(self):
        """


        @return: @rtype:
        """
        return self._cplx_values[self.PARSED_MSG_KEY]

    @property
    def posted_time(self):
        """
        When was the message posted?
        @return: time it was posted in seconds (unix timestamp)
        @rtype: int
        """
        return int(self._values[self.POST_KEY])

    @property
    def formatted_time(self):
        """
        Returns something like "17 Nov 12" or "1h 20m" or "2m"
        @return: A string formatted to display to a user
        @rtype: str
        """
        dt = int(time.time() - self.posted_time)
        posted_seconds = timedelta(seconds=dt)
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
        """


        @return: @rtype:
        """
        return self._values

    def get_complx_dict(self):
        """


        @return: @rtype:
        """
        return self._cplx_values

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

