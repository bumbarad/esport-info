from pathlib import Path
import requests


class Twitch:
    """Holds information about streams and communicates with Twitch API."""

    def __init__(self, credential_path=None):
        """Expects path to file with twitch ID on the first line and twitch secret on the second line. Needed for any
        Twitch API communication!"""
        if credential_path is None:
            credential_path = str(Path(__file__).parent) + "\\static\\twitch_api.txt"

        self.credentials = open(credential_path)
        self.id = self.credentials.readline().strip()
        self.secret = self.credentials.readline().strip()
        self.token = requests.post("https://id.twitch.tv/oauth2/token?client_id={}&client_secret={}&grant_type=client_credentials".format(self.id, self.secret)).json()['access_token']
        self.streams = []

    def query(self, url: str, header=None):
        headers = {'Authorization': 'Bearer ' + self.token, 'Client-Id': self.id}
        if header is not None:
            headers.update(header)
        return requests.get(url, headers=headers).json()

    def get_info_about(self, channel_name: str):
        return self.query("https://api.twitch.tv/helix/search/channels?query=" + channel_name)

    def get_offline_stream_url(self, channel_id: str) -> str:
        videos = self.query("https://api.twitch.tv/helix/videos?user_id=" + channel_id, header={'type': 'archive'})
        return "https://player.twitch.tv/?video=" + videos['data'][0]['id'] + "&parent=127.0.0.1"

    def add_stream(self, channel_name: str):
        self.streams.append(self.get_info_about(channel_name))

    @staticmethod
    def get_channel_id(info: dict) -> str:
        return info['data'][0]['id']

    @staticmethod
    def get_online_stream_url(channel_name: str) -> str:
        return "https://player.twitch.tv/?channel=" + channel_name + "&parent=127.0.0.1"

    @staticmethod
    def is_online(info: dict) -> bool:
        return bool(info['data'][0]['is_live'])
