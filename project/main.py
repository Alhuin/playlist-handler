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
    logger.info('recieved Deezer token request')
    logger.info(f'current_user.deezer_tkn : {current_user.deezer_tkn}')
    if current_user.deezer_tkn:
        logger.info('returning current token')
        return current_user.deezer_tkn, 200
    logger.info('generating new Deezer token')
    auth_url = deezer_client.app_authorization()
    return redirect(auth_url)


@main.route('/soundcloud')
@login_required
def soundcloud_connect():
    logger.info('recieved Soundcloud token request')
    if not soundcloud_client.token_is_valid():
        logger.info('missing or invalid token, generating one')
        soundcloud_client.get_token()
    logger.info(f'returning token : {soundcloud_client.soundcloud_tkn.token}')
    return soundcloud_client.soundcloud_tkn.token if soundcloud_client.soundcloud_tkn else "Error getting token", 200


@main.route('/callback/d')
def deezer_callback():
    logger.info('recieved Deezer oAuth callback')
    authorization_header = deezer_client.user_authorization()
    logger.info(f'Deezer authorization_header : {authorization_header}')
    return authorization_header, 200


@main.route('/')
def index():
    if current_user.is_authenticated:
        logger.info('current_user is authenticated, redirecting to profile')
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
