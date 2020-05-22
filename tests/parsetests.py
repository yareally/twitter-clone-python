from __future__ import print_function
# coding=utf-8
__author__ = 'wes'

import unittest
from libs.parser import Parser


class ParseTests(unittest.TestCase):
    def test_message_parse(self):
        parse = Parser(
            'Ya ya, http://whatever.com @user1 @user2 This is a test, yay http://google.com #woot #blah')
        print(parse.urls)
        print(parse.hashtags)
        print(parse.recipients)
        print(parse.message)

        print(parse._msg_values)
        print(parse._parsed_message)
        print(parse._value_lookup)

        parse = Parser(
            '@tflemings this twitter clone is awful #TwicSuck #awful')
        print(parse.urls)
        print(parse.hashtags)
        print(parse.recipients)
        print(parse.message)
        parse = Parser(
            'Check out this video !!! https://www.youtube.com/watch?v=9hUUsqhetX4 #ps4 #robotorgy')
        print(parse.urls)
        print(parse.hashtags)
        print(parse.recipients)
        print(parse.message)
        print("finally")
        print(parse.formatted_msg)

if __name__ == '__main__':
    unittest.main()
