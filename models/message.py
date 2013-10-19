from collections import OrderedDict


class Message():
    # just the id to reference the message
    id = 0
    # who posted it
    user_id = 0
    # the actual raw message
    message = ''
    # when was it posted?
    timestamp = ''
    # users that favorited the message
    favorite_by = set()
    # users that retweeted the message
    retweet_by = set()
    # users that replied to the message
    replies = OrderedDict
    # any hashtags for the message
    hashtags = set()
    # who is the message to be sent to? (zero or more people)
    recipients = set()

    def __init__(self, user_id, message, timestamp='', favorite_by=set, retweet_by=set, replies=OrderedDict, hashtags=set, recipients=set):
        self.user_id = user_id
        self.message = message
        self.timestamp = timestamp
        self.favorite_by = favorite_by
        self.retweet_by = retweet_by
        self.replies = replies
        self.hashtags = hashtags
        self.recipients = recipients