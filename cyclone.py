from flask import Flask
from tornado.web import RequestHandler, Application, FallbackHandler
from tornado.wsgi import WSGIContainer
from tornado.ioloop import IOLoop
from flask_main import app



class MainHandler(RequestHandler):
    """
    Class for dealing with Tornado web stuff
    """
    def get(self):
        """
        Type http://<server-ip-here>:5000/tornado to access tornado stuff
        @return:
        """
        self.write("Tornado side message")

flask_app = WSGIContainer(app)

application = Application([
    # tornado http request, since the URL has /tornado
    (r"/tornado", MainHandler),
    # pass off to Flask if we're not using tornado
    (r".*", FallbackHandler,
     dict(fallback=flask_app)),], debug=True)

if __name__ == "__main__":
    # Type http://<server-ip-here>:5000 to access flask stuff
    application.listen(5000, '0.0.0.0')
    IOLoop.instance().start()