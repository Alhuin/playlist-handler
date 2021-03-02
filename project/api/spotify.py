import os
import json
import requests
import base64
import urllib.parse as urllibparse
from flask import request
from flask_login import current_user

from project import db


class SpotifyApi:

    def __init__(self):
        # Client Keys
        self.client_id = os.environ["SPOTIFY_CLIENT_ID"]
        self.client_secret = os.environ["SPOTIFY_CLIENT_SECRET"]

        # Spotify URLS
        self.auth_url = "https://accounts.spotify.com/authorize"
        self.token_url = "https://accounts.spotify.com/api/token"
        self.api_url = "https://api.spotify.com/v1"

        # Server-side Parameters
        self.client_side_url = os.environ["CLIENT_SIDE_URL"]
        self.port = os.environ["CLIENT_SIDE_PORT"]
        self.redirect_uri = "{}{}/callback/q".format(
            self.client_side_url,
            ':{}'.format(self.port) if self.port != "False" else ''
        )
        self.scope = "user-library-read"

    # Authorization of application with spotify
    def app_authorization(self):
        auth_query_parameters = {
            "response_type": "code",
            "redirect_uri": self.redirect_uri,
            "scope": self.scope,
            "client_id": self.client_id
        }
        url_args = "&".join(["{}={}".format(key, urllibparse.quote(val)) for key, val in auth_query_parameters.items()])
        auth_url = "{}/?{}".format(self.auth_url, url_args)
        return auth_url

    # User allows us to interact with their account
    def user_authorization(self):
        auth_token = request.args['code']
        code_payload = {
            "grant_type": "authorization_code",
            "code": str(auth_token),
            "redirect_uri": self.redirect_uri
        }
        auth_str = '{}:{}'.format(self.client_id, self.client_secret)
        base64encoded = base64.urlsafe_b64encode(auth_str.encode()).decode()
        headers = {"Authorization": "Basic {}".format(base64encoded)}
        post_request = requests.post(self.token_url, data=code_payload, headers=headers)

        # Tokens are Returned to Application
        response_data = json.loads(post_request.text)
        print(response_data)
        access_token = response_data["access_token"]
        current_user.spotify_tkn = response_data["access_token"]
        db.session.commit()
        refresh_token = response_data["refresh_token"]
        token_type = response_data["token_type"]
        expires_in = response_data["expires_in"]

        # Use the access token to access Spotify API
        authorization_header = {"Authorization": "Bearer {}".format(access_token)}
        return authorization_header

    # Gathering of profile information
    def get_profile_data(self, header):
        user_profile_api_endpoint = "{}/me".format(self.api_url)
        profile_response = requests.get(user_profile_api_endpoint, headers=header)
        profile_data = json.loads(profile_response.text)
        return profile_data

    # Gathering of playlist information
    @staticmethod
    def get_playlist_data(header, profile):
        playlist_api_endpoint = "{}/playlists".format(profile["href"])
        playlists_response = requests.get(playlist_api_endpoint, headers=header)
        playlist_data = json.loads(playlists_response.text)
        return playlist_data

    # Gathering of album information
    @staticmethod
    def get_album_data(header, profile, limit, offset):
        artist_api_endpoint = ("{}/albums?limit=" + str(limit) + "&offset=" + str(offset)).format(profile["href"])
        artist_response = requests.get(artist_api_endpoint, headers=header)
        artist_data = json.loads(artist_response.text)
        return artist_data
