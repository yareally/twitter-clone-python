from redis import StrictRedis
import sockjs.tornado
import tornado.web
from libs.session import RedisSessionStore, Session

class Application(tornado.web.Application):
    def __init__(self, handlers=None, default_host="", transforms=None,
                 wsgi=False, **settings):
        tornado.web.Application.__init__(self, handlers, default_host, transforms, wsgi, **settings)
       # self.db_session = db_session
        self.redis = StrictRedis()
        self.session_store = RedisSessionStore(self.redis)


class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        return self.session['user'] if self.session and 'user' in self.session else None

    @property
    def session(self):
        session_id = self.get_secure_cookie('sid')
        return Session(self.application.session_store, session_id)


class FallbackHandler(BaseHandler):
    """A `RequestHandler` that wraps another HTTP server callback.

    The fallback is a callable object that accepts an
    `~.httpserver.HTTPRequest`, such as an `Application` or
    `tornado.wsgi.WSGIContainer`.  This is most useful to use both
    Tornado ``RequestHandlers`` and WSGI in the same server.  Typical
    usage::

        wsgi_app = tornado.wsgi.WSGIContainer(
            django.core.handlers.wsgi.WSGIHandler())
        application = tornado.web.Application([
            (r"/foo", FooHandler),
            (r".*", FallbackHandler, dict(fallback=wsgi_app),
        ])
    """

    def initialize(self, fallback):
        self.fallback = fallback

    def prepare(self):
        self.fallback(self.request)
        self._finished = True
