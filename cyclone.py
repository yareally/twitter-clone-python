from tornado.web import FallbackHandler
from tornado.wsgi import WSGIContainer
from tornado.ioloop import IOLoop
from flask_main import app
from sockjs.tornado import SockJSRouter, SockJSConnection
from app_wrap import Application


class AsyncConnection(SockJSConnection):
    """Chat connection implementation"""
    # Class level variable

    participants = set()


    def on_open(self, info):
        # Send that someone joined
        self.broadcast(self.participants, "Someone joined.")

        # Add client to the clients list
        self.participants.add(self)


    def on_message(self, message):
        # Broadcast message
        self.broadcast(self.participants, message)


    def on_close(self):
        # Remove client from the clients list and broadcast leave message
        self.participants.remove(self)

        self.broadcast(self.participants, "Someone left.")


if __name__ == "__main__":
    import logging

    logging.getLogger().setLevel(logging.DEBUG)

    flask_app = WSGIContainer(app)
    AsyncRouter = SockJSRouter(AsyncConnection, '/async')

    # pass off to Flask if we're not using tornado for anything other than comet/async
    application = Application([(r".*", FallbackHandler, dict(fallback=flask_app)), ], debug=True)

    # separate app for async stuff
    async_app = Application(AsyncRouter.urls, debug=True)

    # listen for async requests
    # Type http://<server-ip-here>:8080/async to access flask stuff
    async_app.listen(8081)

    # listen for normal web requests
    # Type http://<server-ip-here>:5000 to access flask stuff
    application.listen(5000, '0.0.0.0')
    IOLoop.instance().start()