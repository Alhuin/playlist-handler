import json
import requests
import os
import re
from flask_login import current_user
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium import webdriver
from requests.adapters import HTTPAdapter


class SoundCloudApi:
    def __init__(self):
        self.api_url = "https://api-v2.soundcloud.com"
        self.session = requests.Session()
        self.client_id = os.environ["SOUNDCLOUD_CLIENT_ID"]
        self.session.mount("http://", adapter=HTTPAdapter(max_retries=3))
        self.session.mount("https://", adapter=HTTPAdapter(max_retries=3))

    @staticmethod
    def filter_network_events(event):
        return json.loads(event["message"])["message"]['method'] \
               in ("Network.response", "Network.request", "Network.webSocket")

    def update_client_id(self):
        pattern = re.compile('client_id=(.*?)&')
        cap = DesiredCapabilities.CHROME
        cap['goog:loggingPrefs'] = {'performance': 'ALL'}
        driver = webdriver.Chrome(desired_capabilities=cap)
        driver.get("https://www.soundcloud.com")

        traffic = [
            json.loads(r["message"])["message"]["params"]["request"]["url"] for r in driver.get_log('performance')
            if json.loads(r["message"])["message"]["method"] == 'Network.requestWillBeSent'
        ]

        for request in traffic:
            match = re.search(pattern, request)
            if match:
                os.environ["SOUNDCLOUD_CLIENT_ID"] = self.client_id = match.groups()[0]
                break

        driver.quit()

    def client_id_is_valid(self):
        r = requests.Session().get(
            'https://api-v2.soundcloud.com/featured_tracks/top/all-music',
            params={"client_id": self.client_id}
        )
        return r.status_code == 200

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
            return "{}?client_id={}".format(track["download_url"], current_user.soundcloud_tkn), track.get(
                "original_format", "mp3")
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
