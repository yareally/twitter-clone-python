# coding=utf-8
import re

from orderedset import OrderedSet


class Parser(object):
    """

    @param message: Message to parse
    @type message: str
    """

    __HT_HTML = '<a href="/dash?ht=%s">%s</a>'
    __USER_HTML = '<a href="/dash?user=%s">%s</a>'
    __URL_HTML = '<a href="%s">%s</a>'

    def __init__(self, message):
        self.formatted_msg = ''
        self.message = message
        self._parsed_message, self._msg_values, self._value_lookup = self.parse_msg(message)

    def parse_msg(self, message=''):
        """
        Parses a message removing the tokens and adding a placeholder
        @param message: Message to parse
        @type message: str
        @return: The parsed message with placeholders and removed token values
        @rtype: (str, dict, dict(set)))
        """
        message = message if message else self.message

        msg_values = {}
        value_lookup = {'recipients': OrderedSet(), 'hashtags': OrderedSet(), 'urls': OrderedSet()}

        pattern = re.compile(
            r'(?P<recipients>@[\w\-]+)|(?P<hashtags>#[\w\-]+)|\b(?P<urls>(?:https?|ftp|file)://[-A-Za-z0-9+&@#/%?=~_|$!:,.;]*[a-zA-Z0-9+&@#/%=~_|$])',
            re.I)

        for match in pattern.finditer(message):

            for k, v in match.groupdict().items():
                if v is None:
                    continue
                token = '{%s_%d}' % (k, match.start())
                fmt_token = ''

                if k == 'hashtags':
                    #message = message.replace(v, '{%s_%d}' % (k, match.start()))
                    fmt_token = self.__HT_HTML % (token, token)

                elif k == 'recipients':
                    fmt_token = self.__USER_HTML % (token, token)

                elif k == 'urls':
                    fmt_token = self.__URL_HTML % (token, token)

                message = message.replace(v, fmt_token)

                msg_values['%s_%d' % (k, match.start())] = v
                value_lookup[k].add(v)

        # puts everything back in.
        # @see http://docs.python.org/2/library/string.html#string-formatting
        print(message.format(**msg_values))
        self.formatted_msg = message.format(**msg_values)
        return message, msg_values, value_lookup

    @property
    def urls(self):
        """
        Gets the urls for a message
        @return: the urls
        @rtype: set
        """
        return set(self._msg_values.values()).intersection(self._value_lookup['urls'])

    @property
    def hashtags(self):
        """
        Gets the hashtags for a message
        @return: the hashtags
        @rtype: set
        """
        return set(self._msg_values.values()).intersection(self._value_lookup['hashtags'])

    @property
    def recipients(self):
        """
        Gets the intended (if any) recipients for a message. By default all followers are notified.
        This is just for any additional ones included in the tweet (via @username)
        @return: the recipients
        @rtype: set
        """
        return set(self._msg_values.values()).intersection(self._value_lookup['recipients'])

    @property
    def parsed_msg(self):
        """
        Gets the message with placeholder instead of the recipients/hashtags/urls
        @return: the parsed message string
        @rtype: str
        """
        return self.parsed_msg
