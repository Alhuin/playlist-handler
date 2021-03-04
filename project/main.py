import logging
from flask import Blueprint, render_template, redirect
from flask_login import login_required, current_user
from .api import spotify, deezer, soundcloud

main = Blueprint('main', __name__)
logger = logging.getLogger(__name__)
logger.info('init api clients')

spotify_client = spotify.SpotifyApi()
deezer_client = deezer.DeezerApi()
soundcloud_client = soundcloud.SoundCloudApi()


@main.route('/spotify')
@login_required
def spotify_connect():
    logger.info('recieved Spotify token request')
    logger.info(f'current_user.spotify_token : {current_user.spotify_tkn}')
    if current_user.spotify_tkn:
        # TODO check is valid
        logger.info('returning current token')
        return current_user.spotify_tkn, 200
    logger.info('generating Spotify token')
    auth_url = spotify_client.app_authorization()
    return redirect(auth_url)


@main.route('/callback/q')
def spotify_callback():
    logger.info('recieved Spotify oAuth callback')
    authorization_header = spotify_client.user_authorization()
    logger.info(f'Spotify authorization_header : {authorization_header}')

    return authorization_header, 200


@main.route('/deezer')
@login_required
def deezer_connect():
    if current_user.deezer_tkn:
        # TODO check is valid
        return current_user.deezer_tkn, 200
    auth_url = deezer_client.app_authorization()
    return redirect(auth_url)


@main.route('/callback/d')
def deezer_callback():
    authorization_header = deezer_client.user_authorization()
    return authorization_header, 200


@main.route('/soundcloud')
@login_required
def soundcloud_connect():
    if not soundcloud_client.client_id_is_valid():
        soundcloud_client.update_client_id()
    return soundcloud_client.client_id


@main.route('/')
def index():
    if current_user.is_authenticated:
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
