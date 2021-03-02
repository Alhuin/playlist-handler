import os
import json
import requests
import urllib.parse as urllibparse
from flask import request
from flask_login import current_user
from project import db, User


class DeezerApi:

    def __init__(self):
        # Client Keys
        self.client_id = os.environ["DEEZER_CLIENT_ID"]
        self.client_secret = os.environ["DEEZER_CLIENT_SECRET"]

        # Deezer URLS
        self.auth_url = "https://connect.deezer.com/oauth/auth.php"
        self.token_url = "https://connect.deezer.com/oauth/access_token.php"
        self.api_url = "https://api.deezer.com"

        # Server-side Parameters
        self.client_side_url = os.environ["CLIENT_SIDE_URL"]
        self.port = os.environ["CLIENT_SIDE_PORT"]
        self.redirect_uri = "{}{}/callback/d".format(
            self.client_side_url,
            ':{}'.format(self.port) if self.port != "False" else ''
        )

    # Authorization of application with deezer
    def app_authorization(self):
        auth_query_parameters = {
            "app_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "perms": "basic_access,email",
        }
        url_args = "&".join(["{}={}".format(key, urllibparse.quote(val)) for key, val in auth_query_parameters.items()])
        auth_url = "{}/?{}".format(self.auth_url, url_args)
        return auth_url

    # User allows us to access to their deezer account
    def user_authorization(self):
        auth_token = request.args['code']
        code_payload = {
            "app_id": self.client_id,
            "secret": self.client_secret,
            "code": auth_token,
            "output": json
        }
        post_request = requests.post(self.token_url, data=code_payload)

        # Token & expiration
        response_data = urllibparse.parse_qs(post_request.text)
        access_token = response_data["access_token"]
        current_user.deezer_tkn = response_data["access_token"]
        db.session.commit()
        token_expires = response_data["expires"]
        # Use the access token to access Spotify API
        authorization_header = {"Authorization": "Bearer {}".format(access_token)}
        return authorization_header
