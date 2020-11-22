from pathlib import Path
import flask
from flask import Flask, render_template, url_for
from flask_restplus import Api, Resource
from twitch import Twitch
import requests

app = Flask(__name__)
api_bp = flask.Blueprint("api", __name__, url_prefix="/api")
api = Api(api_bp, title="Esports-info API", version="1.0", doc="/docs")
app.register_blueprint(api_bp)


twitch_id = ""
twitch_token = ""
channels = ["esl_csgo", "dreamhackcs"]


@api.route('/info/<string:name>', endpoint='info')
@api.doc(params={'name': 'Name of target twitch account.'})
class InfoAPI(Resource):
    def get(self, name):
        return {"data": name}


# @api.route('/custom/<string:name>', endpoint='info')
# @api.doc(params={'name': 'Name of target twitch account.'})
# class CreateCustomPageAPI(Resource):
#     def post(self, name):
#         return {"data": name}


def authorized_twitch_query(url: str, header=None):
    headers = {'Authorization': 'Bearer ' + twitch_token, 'Client-Id': twitch_id}
    if header is not None:
        headers.update(header)
    return requests.get(url, headers=headers).json()


def get_info_about_twitch_stream(name: str):
    return authorized_twitch_query("https://api.twitch.tv/helix/search/channels?query=" + name)


def is_online(info: dict) -> bool:
    return bool(info['data'][0]['is_live'])


def parse_team_names(title: str) -> list:
    teams = []
    ret = []
    for team in teams:
        if title.find(team):
            ret.append(team)
    return ret


def my_renderer(html: str, this: int):
    twitch_data = []
    online_streams = []
    teams = []
    for i in range(len(channels)):
        twitch_data.append(get_info_about_twitch_stream(channels[i]))
        online_streams.append(is_online(twitch_data[i]))

    if this != -1:
        if online_streams[this]:
            stream = "https://player.twitch.tv/?channel=" + channels[this] + "&parent=127.0.0.1"
            # teams = parse_team_names(twitch_data[this]['data'][0]['title'])
        else:
            videos = authorized_twitch_query("https://api.twitch.tv/helix/videos?user_id="
                                             + twitch_data[this]['data'][0]['id'], header={'type': 'archive'})
            stream = "https://player.twitch.tv/?video=" + videos['data'][0]['id'] + "&parent=127.0.0.1"
        return render_template(html, online_streams=online_streams, is_online=online_streams[this], stream=stream)
    else:
        return render_template(html, online_streams=online_streams, stream=False)


@app.route('/')
def index():
    return my_renderer("index.html", -1)


@app.route('/esl')
def esl():
    return my_renderer("esl.html", 0)


@app.route('/dreamhack')
def dreamhack():
    return my_renderer("dreamhack.html", 1)


if __name__ == "__main__":
    twitch_credentials = open(str(Path(__file__).parent) + "\\static\\twitch_api.txt")
    twitch_id = twitch_credentials.readline().strip()
    twitch_secret = twitch_credentials.readline().strip()

    twitch_token_url = "https://id.twitch.tv/oauth2/token?client_id={}&client_secret={}&grant_type=client_credentials"
    twitch_token = requests.post(twitch_token_url.format(twitch_id, twitch_secret)).json()['access_token']

    app.run(debug=True, )
