from pathlib import Path
import requests


class Twitch:
    """Holds information about streams and communicates with Twitch API."""

    def __init__(self, credential_path=None):
        """Expects path to file with twitch ID on the first line and twitch secret on the second line. Needed for any
        Twitch API communication!"""
        if credential_path is None:
            credential_path = str(Path(__file__).parent) + "\\static\\twitch_api.txt"

        self.__credentials = open(credential_path)
        self.__id = self.__credentials.readline().strip()
        self.__secret = self.__credentials.readline().strip()
        self.__token = requests.post("https://id.twitch.tv/oauth2/token?client_id={}&client_secret={}&grant_type=client_credentials".format(self.__id, self.__secret)).json()['access_token']
        self.streams = {}

    def __query(self, url: str, header=None):
        headers = {'Authorization': 'Bearer ' + self.__token, 'Client-Id': self.__id}
        if header is not None:
            headers.update(header)
        return requests.get(url, headers=headers).json()

    def get_info_about(self, channel_name: str):
        return self.__query("https://api.twitch.tv/helix/search/channels?query=" + channel_name)

    def __get_offline_stream_url(self, channel_id: str) -> str:
        videos = self.__query("https://api.twitch.tv/helix/videos?user_id=" + channel_id, header={'type': 'archive'})
        return "https://player.twitch.tv/?video=" + videos['data'][0]['id'] + "&parent=127.0.0.1"

    def add_stream(self, channel_name: str):
        info = self.get_info_about(channel_name)
        if len(info['data']) > 0:
            self.streams[info['data'][0]['display_name']] = info['data'][0]
            self.streams[info['data'][0]['display_name']]['static'] = False

    def get_stream_url(self, channel_name: str) -> str:
        if self.is_online(self.streams[channel_name]):
            return self.__get_online_stream_url(channel_name)
        return self.__get_offline_stream_url(self.get_channel_id(self.streams[channel_name]))

    @staticmethod
    def get_channel_id(info: dict) -> str:
        return info['id']

    @staticmethod
    def __get_online_stream_url(channel_name: str) -> str:
        return "https://player.twitch.tv/?channel=" + channel_name + "&parent=127.0.0.1"

    @staticmethod
    def is_online(info: dict) -> bool:
        return bool(info['is_live'])

    def refresh_streams(self):
        for key in self.streams.keys():
            static = self.streams[key]['static']
            nm = self.streams[key]['display_name']
            banner = None
            if 'banner' in self.streams[key]:
                banner = self.streams[key]['banner']
            self.add_stream(key)
            self.streams[key]['static'] = static
            self.streams[key]['display_name'] = nm
            if banner is not None:
                self.streams[key]['banner'] = banner
