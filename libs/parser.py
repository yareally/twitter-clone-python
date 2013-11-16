# coding=utf-8
import re

class Parser(object):

    """

    @param message: Message to parse
    @type message: str
    """

    def __init__(self, message):
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
        value_lookup = {'recipients': set(), 'hashtags': set(), 'urls': set()}

        pattern = re.compile(
            r'(?P<recipients>@[\w\-]+)|(?P<hashtags>#[\w\-]+)|\b(?P<urls>(?:https?|ftp|file)://[-A-Za-z0-9+&@#/%?=~_|$!:,.;]*[a-zA-Z0-9+&@#/%=~_|$])', re.I)

        for match in pattern.finditer(message):

            for k,v in match.groupdict().items():
                if v is None:
                    continue

                message = message.replace(v, '{%s_%d}' % (k, match.start()))
                msg_values['%s_%d' % (k, match.start())] = v
                value_lookup[k].add(v)

        return message, msg_values, value_lookup

    @property
    def urls(self):
        return set(self._msg_values.values()).intersection(self._value_lookup['urls'])

    @property
    def hashtags(self):
        return set(self._msg_values.values()).intersection(self._value_lookup['hashtags'])

    @property
    def recipients(self):
        return set(self._msg_values.values()).intersection(self._value_lookup['recipients'])