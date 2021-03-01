import os
import json
import requests
import urllib.parse as urllibparse
from flask import request

# Client Keys
CLIENT_ID = os.environ["DEEZER_CLIENT_ID"]
CLIENT_SECRET = os.environ["DEEZER_CLIENT_SECRET"]

# Deezer URLS
DEEZER_AUTH_URL = "https://connect.deezer.com/oauth/auth.php"
DEEZER_TOKEN_URL = "https://connect.deezer.com/oauth/access_token.php"
DEEZER_API_BASE_URL = "https://api.deezer.com"

# Server-side Parameters
CLIENT_SIDE_URL = os.environ["CLIENT_SIDE_URL"]
PORT = os.environ["CLIENT_SIDE_PORT"]
REDIRECT_URI = "{}{}/callback/d".format(CLIENT_SIDE_URL, ':{}'.format(PORT) if PORT != "False" else '')


# Authorization of application with deezer
def app_authorization():
    auth_query_parameters = {
        "app_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "perms": "basic_access,email",
    }
    url_args = "&".join(["{}={}".format(key, urllibparse.quote(val)) for key, val in auth_query_parameters.items()])
    auth_url = "{}/?{}".format(DEEZER_AUTH_URL, url_args)
    return auth_url


# User allows us to access to their deezer account
def user_authorization():
    auth_token = request.args['code']
    code_payload = {
        "app_id": CLIENT_ID,
        "secret": CLIENT_SECRET,
        "code": auth_token,
        "output": json
    }
    post_request = requests.post(DEEZER_TOKEN_URL, data=code_payload)

    # Tokens are Returned to Application
    print(post_request.text)
    response_data = urllibparse.parse_qs(post_request.text)
    print(response_data)
    access_token = response_data["access_token"]
    token_expires = response_data["expires"]

    # Use the access token to access Spotify API
    authorization_header = {"Authorization": "Bearer {}".format(access_token)}
    return authorization_header
