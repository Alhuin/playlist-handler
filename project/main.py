from flask import Blueprint, render_template, redirect
from flask_login import login_required, current_user
from .api import spotify, deezer
from . import db

main = Blueprint('main', __name__)


@main.route('/spotify')
def spotify_connect():
    auth_url = spotify.app_authorization()
    return redirect(auth_url)


@main.route('/callback/q')
def spotify_callback():
    authorization_header = spotify.user_authorization()

    profile_data = spotify.get_profile_data(authorization_header)
    print("PROFILE DATA")
    print(profile_data)

    playlist_data = spotify.get_playlist_data(authorization_header, profile_data)
    print("PLAYLIST DATA")
    print(playlist_data)

    artist_data = spotify.get_album_data(authorization_header, profile_data, 50, 0)
    print("ARTIST DATA")
    print(artist_data)

    return "callback"


@main.route('/deezer')
def deezer_connect():
    auth_url = deezer.app_authorization()
    return redirect(auth_url)


@main.route('/callback/d')
def deezer_callback():
    authorization_header = deezer.user_authorization()
    print(authorization_header)
    return "callback"


@main.route('/')
def index():
    return render_template('index.html')


@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html', name=current_user.name)
