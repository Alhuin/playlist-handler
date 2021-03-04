import re
import logging
from pprint import pprint

from flask_login import current_user
from seleniumwire import webdriver
import json, requests
from requests.adapters import HTTPAdapter

from project import db, SoundcloudToken

logger = logging.getLogger(__name__)


class SoundCloudApi:
    def __init__(self):
        self.api_url = "https://api-v2.soundcloud.com"
        self.session = requests.Session()
        self.soundcloud_tkn = False
        self.session.mount("http://", adapter=HTTPAdapter(max_retries=3))
        self.session.mount("https://", adapter=HTTPAdapter(max_retries=3))

    def token_is_valid(self):
        soundcloud_tkn = SoundcloudToken.query.first()
        logger.info(f'Checking if db token is valid: {soundcloud_tkn}')
        r = requests.Session().get(
            f'{self.api_url}/resolve',
            params={"client_id": soundcloud_tkn, 'url': 'https://soundcloud.com/eminemofficial'}
        )
        logger.info(f'request return status code {r.status_code}')
        return r.status_code == 200

    def get_token(self):
        soundcloud_tkn = SoundcloudToken.query.first()
        logger.info(f'DB SouncloudId : {soundcloud_tkn}')
        logger.info(f'Scraping new soundcloud client_id')
        options = webdriver.ChromeOptions()
        pattern = re.compile('client_id=(.*?)&')
        driver = webdriver.Chrome(chrome_options=options)
        driver.get("https://www.soundcloud.com")

        for request in driver.requests:
            m = re.search(pattern, request.url)
            if m:
                if not soundcloud_tkn:
                    logger.info(f'creating new soundcloud token in db: {m.groups()[0]}')
                    soundcloud_tkn = SoundcloudToken(m.groups()[0])
                    db.session.add(soundcloud_tkn)
                    self.soundcloud_tkn = soundcloud_tkn
                else:
                    logger.info(f'editing soundcloud token in db: {m.groups()[0]}')
                    self.soundcloud_tkn.token = m.groups()[0]
                db.session.commit()
                break
        driver.quit()

    def get_uploaded_tracks(self, user_id, limit=9999):
        url_params = {
            "client_id": self.soundcloud_tkn.token,
            "limit": limit,
            "offset": 0
        }
        url = "{}/users/{}/tracks".format(self.api_url, user_id)
        response = self.session.get(url, params=url_params)
        json_payload = json.loads(response.text)
        tracks = json_payload["collection"]
        return tracks

    def get_liked_tracks(self, user_id, nb_tracks=10):
        url_params = {
            "client_id": self.soundcloud_tkn.token,
            "limit": nb_tracks,
            "offset": 0
        }
        url = "{}/users/{}/likes".format(self.api_url, user_id)
        response = self.session.get(url, params=url_params)
        json_payload = json.loads(response.text)
        tracks = filter(lambda x: 'playlist' not in x, json_payload["collection"])
        return list(map(lambda x: x['track'], tracks))

    def get_recommended_tracks(self, track, nb_tracks=10):
        url_params = {
            "client_id": self.soundcloud_tkn,
            "limit": nb_tracks,
            "offset": 0
        }
        recommended_tracks_url = "{}/tracks/{}/related".format(self.api_url, track.id)
        r = self.session.get(recommended_tracks_url, params=url_params)
        tracks = json.loads(r.text)["collection"]
        tracks = map(lambda x: x["track"], tracks[:nb_tracks])
        return list(tracks)

    def get_charted_tracks(self, kind, genre, limit=9999):
        url_params = {
            "limit": limit,
            "genre": "soundcloud:genres:" + genre,
            "kind": kind,
            "client_id": self.soundcloud_tkn
        }
        url = "{}/charts".format(self.api_url)
        response = self.session.get(url, params=url_params)
        json_payload = json.loads(response.text)
        tracks = json_payload["collection"]
        return tracks

    def get_track_url(self, track):
        if track["downloadable"] and "download_url" in track:
            return "{}?client_id={}".format(track["download_url"], current_user.soundcloud_tkn), track.get("original_format", "mp3")
        if track["streamable"]:
            if "stream_url" in track:
                return "{}?client_id={}".format(track["stream_url"], current_user.soundcloud_tkn), "mp3"
            for transcoding in track["media"]["transcodings"]:
                if transcoding["format"]["protocol"] == "progressive":
                    r = self.session.get(transcoding["url"], params={"client_id": current_user.soundcloud_tkn})
                    return json.loads(r.text)["url"], "mp3"
        return None, None

    def get_track_metadata(self, track):
        artist = "unknown"
        if "publisher_metadata" in track and track["publisher_metadata"]:
            artist = track["publisher_metadata"].get("artist", "")
        elif "user" in track or not artist:
            artist = track["user"]["username"]
        url, file_format = self.get_track_url(track)
        return {
            "title": str(track.get("title", track["id"])),
            "artist": artist,
            "year": str(track.get("release_year", "")),
            "genre": str(track.get("genre", "")),
            "format": file_format,
            "download_url": url,
            "artwork_url": track["artwork_url"]
        }

    def get_user(self, profile_url):
        r = self.session.get(
            '{}/resolve'.format(self.api_url),
            params={"client_id": self.soundcloud_tkn, 'url': profile_url}
        )
        if r.status_code != 200:
            return False
        user = json.loads(r.text)
        return user
