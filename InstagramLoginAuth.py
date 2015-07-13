# -*- coding: utf-8 -*-
import tornado.httputil
import tornado.httpclient
import tornado.web
import tornado.gen
from tornado.auth import AuthError
import urllib
from tornado.concurrent import return_future
from tornado.auth import _auth_return_future
from tornado import escape
import functools


class InstagramMixin(object):
    @return_future
    def authorize_redirect(self, redirect_uri=None, client_id=None,
                           client_secret=None, extra_params=None,
                           callback=None, scope=None, response_type="code"):
        args = {
            'client_id': client_id,
            'redirect_uri': redirect_uri,
            'response_type': response_type
        }
        if scope:
            args['scope'] = ' '.join(scope)

        self.redirect(
            tornado.httputil.url_concat(self._OAUTH_AUTHORIZE_URL, args))   # Jump to auth page
        callback()

    def _oauth_request_token_url(self, redirect_uri=None, client_id=None, client_secret=None, code=None):
        url = self._OAUTH_ACCESS_TOKEN_URL
        args = dict(
            client_id=client_id,
            redirect_uri=redirect_uri,
            client_secret=client_secret,
            grant_type="authorization_code",
            code=code
        )
        return tornado.httputil.url_concat(url, args)

class InstagramOAuth2Mixin(InstagramMixin):
    _OAUTH_ACCESS_TOKEN_URL = "https://api.instagram.com/oauth/access_token"
    _OAUTH_AUTHORIZE_URL = "https://api.instagram.com/oauth/authorize/"
    _OAUTH_VERSION = "2.0"

    def get_auth_http_client(self):
        return tornado.httpclient.AsyncHTTPClient()

    @_auth_return_future
    def get_authenticated_user(self, redirect_uri, code, callback):
        http = self.get_auth_http_client()
        body = urllib.urlencode({
            'redirect_uri': redirect_uri,
            'code': code,
            'client_id': self.settings['instagram_client_id'],
            'client_secret': self.settings['instagram_client_secret'],
            "grant_type": "authorization_code",
            })

        http.fetch(self._OAUTH_ACCESS_TOKEN_URL, functools.partial(self._on_access_token, callback),
                   method="POST", body=body)

    def _on_access_token(self, future, response):
        if response.error:
            future.set_exception(AuthError('Instagram Auth Error: %s' % str(response)))
            return
        args = escape.json_decode(response.body)
        future.set_result(args)
