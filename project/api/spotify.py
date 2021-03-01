import os
import json
import requests
import base64
import urllib.parse as urllibparse
from flask import request


# Client Keys
CLIENT_ID = os.environ["SPOTIFY_CLIENT_ID"]
CLIENT_SECRET = os.environ["SPOTIFY_CLIENT_SECRET"]

# Spotify URLS
SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_API_BASE_URL = "https://api.spotify.com"
API_VERSION = "v1"
SPOTIFY_API_URL = "{}/{}".format(SPOTIFY_API_BASE_URL, API_VERSION)

# Server-side Parameters
CLIENT_SIDE_URL = os.environ["CLIENT_SIDE_URL"]
PORT = os.environ["CLIENT_SIDE_PORT"]
REDIRECT_URI = "{}{}/callback/q".format(CLIENT_SIDE_URL, ':{}'.format(PORT) if PORT != "False" else '')
SCOPE = "user-library-read"
STATE = ""
SHOW_DIALOG_bool = True
SHOW_DIALOG_str = str(SHOW_DIALOG_bool).lower()


# Authorization of application with spotify
def app_authorization():
    auth_query_parameters = {
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        "scope": SCOPE,
        "client_id": CLIENT_ID
    }
    url_args = "&".join(["{}={}".format(key, urllibparse.quote(val)) for key, val in auth_query_parameters.items()])
    auth_url = "{}/?{}".format(SPOTIFY_AUTH_URL, url_args)
    return auth_url


# User allows us to acces there spotify
def user_authorization():
    auth_token = request.args['code']
    code_payload = {
        "grant_type": "authorization_code",
        "code": str(auth_token),
        "redirect_uri": REDIRECT_URI
    }
    auth_str = '{}:{}'.format(CLIENT_ID, CLIENT_SECRET)
    base64encoded = base64.urlsafe_b64encode(auth_str.encode()).decode()
    headers = {"Authorization": "Basic {}".format(base64encoded)}
    post_request = requests.post(SPOTIFY_TOKEN_URL, data=code_payload, headers=headers)

    # Tokens are Returned to Application
    response_data = json.loads(post_request.text)
    print(response_data)
    access_token = response_data["access_token"]
    refresh_token = response_data["refresh_token"]
    token_type = response_data["token_type"]
    expires_in = response_data["expires_in"]

    # Use the access token to access Spotify API
    authorization_header = {"Authorization": "Bearer {}".format(access_token)}
    return authorization_header


# Gathering of profile information
def get_profile_data(header):
    # Get user profile data
    user_profile_api_endpoint = "{}/me".format(SPOTIFY_API_URL)
    profile_response = requests.get(user_profile_api_endpoint, headers=header)
    profile_data = json.loads(profile_response.text)
    return profile_data


# Gathering of playlist information
def get_playlist_data(header, profile):
    # Get user playlist data
    playlist_api_endpoint = "{}/playlists".format(profile["href"])
    playlists_response = requests.get(playlist_api_endpoint, headers=header)
    playlist_data = json.loads(playlists_response.text)
    return playlist_data


# Gathering of album information
def get_album_data(header, profile, limit, offset):
    # Get user albums data
    artist_api_endpoint = ("{}/albums?limit=" + str(limit) + "&offset=" + str(offset)).format(profile["href"])
    artist_response = requests.get(artist_api_endpoint, headers=header)
    artist_data = json.loads(artist_response.text)
    return artist_data
