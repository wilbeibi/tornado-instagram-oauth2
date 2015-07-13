# -*- coding: utf-8 -*-
import os
import tornado.web
import tornado.gen
import tornado.httpserver
import tornado.ioloop
from InstagramLoginAuth import InstagramOAuth2Mixin
from tornado.options import define, options


define("port", default=8000, help="run on the given port", type=int)


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", HomeHandler),
            (r"/auth/instagram", AuthLoginHandler),
            (r"/auth/logout", AuthLogoutHandler),
            ]
        settings = dict(
            blog_title = "test tornado blog",
            template_path = os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            instagram_client_id='FILL IN YOUR CLIENT ID',
            instagram_client_secret='FILL IN YOUR CLIENT SECRET',
            redirect_uri='FILL IN YOUR REDIRECT URI',
            login_url="/auth/instagram",
            cookie_secret="FILL IN YOUR COOKIE SECRET",
            xsrf_cookies=True,
            debug=True,
            )
        self.user_info = {}
        tornado.web.Application.__init__(self, handlers, **settings)

class BaseHandle(tornado.web.RequestHandler):
    def get_current_user(self):
        return self.get_secure_cookie("user_id")

class HomeHandler(BaseHandle):
    @tornado.web.authenticated
    def get(self):
        self.write("Auth Success " + self.application.user_info["user"]["username"] + "!")

class AuthLogoutHandler(BaseHandle):
    def get(self):
        self.clear_cookie("user_id")
        self.redirect(self.get_argument("next", "/"))

class AuthLoginHandler(InstagramOAuth2Mixin, tornado.web.RequestHandler):
    @tornado.gen.coroutine
    def get(self):
        if self.get_argument('code', False):
            token = yield self.get_authenticated_user(
                redirect_uri=self.settings['redirect_uri'],
                code=self.get_argument('code')
            )
            if token:
                self.set_secure_cookie("user_id", "ilovewilbeibi~~~")
                self.application.user_info["user"] = token["user"]
                #self.redirect(self.get_argument("next", "/"))
                self.redirect("/")
        else:
            yield self.authorize_redirect(
                redirect_uri=self.settings['redirect_uri'],
                client_id=self.settings['instagram_client_id'],
                scope=None, # used default scope
                response_type='code'
            )


def main():
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()
