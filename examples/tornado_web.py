from tornado.options import options
from tornado.ioloop import IOLoop
from tornado.web import RequestHandler, Application
from tornado_sqlalchemy import SessionMixin, make_session_factory


class WebRequestHandler(RequestHandler, SessionMixin):
    def get(self):
        # do something with self.session
        self.write('Hello, World!')


class WebApplication(Application):
    def __init__(self, *args, **kwargs):
        self.session_factory = make_session_factory(options.database_url)

        handlers = [
            (r'/hello', WebRequestHandler)
        ]

        settings = {'cookie_secret': 'hunter2'}

        super(WebApplication, self).__init__(handlers, **settings)


if __name__ == '__main__':
    WebApplication().listen(8888)
    IOLoop.current().start()
