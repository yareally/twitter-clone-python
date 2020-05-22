# coding=utf-8
__author__ = 'wes'
from redis import StrictRedis
from sockjs.tornado import SockJSRouter
import tornado.web
from libs.session import RedisSessionStore, Session

class Application(tornado.web.Application):
    """

    @param handlers:
    @param default_host:
    @param transforms:
    @param wsgi:
    @param settings:
    """

    def __init__(self, handlers=None, default_host="", transforms=None, wsgi=False, **settings):
        tornado.web.Application.__init__(self, handlers, default_host, transforms, wsgi, **settings)
       # self.db_session = db_session
        self.redis = StrictRedis()
        self.session_store = RedisSessionStore(self.redis)


class BaseHandler(tornado.web.RequestHandler):
    """

    """
    def get_current_user(self):
        """


        @return:
        """
        return self.session['user'] if self.session and 'user' in self.session else None

    @property
    def session(self):
        """


        @return:
        """
        session_id = self.get_secure_cookie('JSESSIONID')
        return Session(self.application.session_store, session_id)

class SocksJsBaseHandler(SockJSRouter):
    """

    """
