# coding=utf-8
__author__ = 'admin'

import unittest
from libs.parser import Parser

class ParseTests(unittest.TestCase):
    def test_message_parse(self):
        parse = Parser(
            'Ya ya, http://whatever.com @user1 @user2 This is a test, yay http://google.com #woot #blah')
        print(parse.urls)


if __name__ == '__main__':
    unittest.main()
