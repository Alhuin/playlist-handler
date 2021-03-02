from flask import Blueprint, render_template, redirect
from flask_login import login_required, current_user
from .api import spotify, deezer, soundcloud
from . import db

main = Blueprint('main', __name__)

spotify_client = spotify.SpotifyApi()
deezer_client = deezer.DeezerApi()
soundcloud_client = soundcloud.SoundCloudApi()


@main.route('/spotify')
def spotify_connect():
    auth_url = spotify_client.app_authorization()
    return redirect(auth_url)


@main.route('/callback/q')
def spotify_callback():
    authorization_header = spotify_client.user_authorization()

    profile_data = spotify_client.get_profile_data(authorization_header)
    print("PROFILE DATA")
    print(profile_data)

    playlist_data = spotify_client.get_playlist_data(authorization_header, profile_data)
    print("PLAYLIST DATA")
    print(playlist_data)

    artist_data = spotify_client.get_album_data(authorization_header, profile_data, 50, 0)
    print("ARTIST DATA")
    print(artist_data)

    return "callback"


@main.route('/deezer')
def deezer_connect():
    auth_url = deezer_client.app_authorization()
    return redirect(auth_url)


@main.route('/callback/d')
def deezer_callback():
    authorization_header = deezer_client.user_authorization()
    print(authorization_header)
    return "callback"


@main.route('/')
def index():
    return render_template('index.html')


@main.route('/home')
@login_required
def home():
    return render_template('home.html', name=current_user.name)


@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html', name=current_user.name)
