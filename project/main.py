from flask import Blueprint, render_template, redirect, current_app
from flask_login import login_required, current_user
from .api import spotify, deezer, soundcloud
from . import db

main = Blueprint('main', __name__)

current_app.logger.info('init api clients')
spotify_client = spotify.SpotifyApi()
deezer_client = deezer.DeezerApi()
soundcloud_client = soundcloud.SoundCloudApi()


@main.route('/spotify')
@login_required
def spotify_connect():
    current_app.logger.info('recieved Spotify token request')
    current_app.logger.info(f'current_user.spotify_token : {current_user.spotify_tn}')
    if current_user.spotify_tkn != 'false':
        current_app.logger.info('returning current token')
        return current_user.spotify_tkn
    current_app.logger.info('generating Spotify token')
    auth_url = spotify_client.app_authorization()
    return redirect(auth_url)


@main.route('/callback/q')
def spotify_callback():
    current_app.logger.info('recieved Spotify oAuth callback')
    authorization_header = spotify_client.user_authorization()
    current_app.logger.info(f'Spotify authorization_header : {authorization_header}')

    return authorization_header, 200


@main.route('/deezer')
@login_required
def deezer_connect():
    current_app.logger.info('recieved Deezer token request')
    current_app.logger.info(f'current_user.spotify_tkn : {current_user.spotify_tn}')
    if current_user.deezer_tkn != 'false':
        current_app.logger.info('returning current token')
        return current_user.deezer_tkn
    current_app.logger.info('generating new Deezer token')
    auth_url = deezer_client.app_authorization()
    return redirect(auth_url)


@main.route('/soundcloud')
@login_required
def soundcloud_connect():
    current_app.logger.info('recieved Soundcloud token request')
    if current_user.soundcloud_tkn != 'false':
        current_app.logger.info(f'current_user.soundcloud_tkn : {current_user.spotify_tn}')
        return current_user.soundcloud_tkn
    current_app.logger.info('generating new Soundcloud token')
    soundcloud_client.check_client_id()
    return f'Soundcloud Callback {current_user.soundcloud_tkn}', 200


@main.route('/callback/d')
def deezer_callback():
    current_app.logger.info('recieved Deezer oAuth callback')
    authorization_header = deezer_client.user_authorization()
    current_app.logger.info(f'Deezer authorization_header : {authorization_header}')
    return authorization_header, 200


@main.route('/')
def index():
    if current_user.is_authenticated:
        current_app.logger.info('current_user is authenticated, redirecting to profile')
        return render_template('profile.html', name=current_user.name)
    return render_template('index.html')


@main.route('/home')
@login_required
def home():
    return render_template('home.html', name=current_user.name)


@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html', name=current_user.name)
