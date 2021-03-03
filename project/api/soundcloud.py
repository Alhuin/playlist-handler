import re
import os
import chromedriver_binary
from flask_login import current_user
from seleniumwire import webdriver
import json, requests
from requests.adapters import HTTPAdapter

from project import db


class SoundCloudApi:
    def __init__(self):
        self.api_url = "https://api-v2.soundcloud.com"
        self.session = requests.Session()
        self.session.mount("http://", adapter=HTTPAdapter(max_retries=3))
        self.session.mount("https://", adapter=HTTPAdapter(max_retries=3))

    def check_client_id(self):
        if not self.get_user('https://soundcloud.com/eminemofficial'):
            options = webdriver.ChromeOptions()
            options.add_argument(" — disable - gpu")
            options.add_argument(" — no - sandbox")
            options.add_argument(' — headless')
            options.add_argument("--remote-debugging-port=9222")

            pattern = re.compile('client_id=(.*?)&')
            driver = webdriver.Chrome(chrome_options=options)
            driver.get("https://www.soundcloud.com")

            for request in driver.requests:
                m = re.search(pattern, request.url)
                if m:
                    current_user.soundcloud_tkn = m.groups()[0]
                    db.session.commit()
                    break
            driver.close()

    def get_uploaded_tracks(self, user_id, limit=9999):
        url_params = {
            "client_id": current_user.soundcloud_tkn,
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
            "client_id": current_user.soundcloud_tkn,
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
            "client_id": current_user.soundcloud_tkn,
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
            "client_id": current_user.soundcloud_tkn
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
            params={"client_id": current_user.soundcloud_tkn, 'url': profile_url}
        )
        if r.status_code != 200:
            return False
        user = json.loads(r.text)
        return user
