import flask
from flask import Flask, render_template, make_response, jsonify, redirect, url_for, request
from flask_restplus import Api, Resource, fields
from twitch import Twitch
from liquipedia import Liquipedia
import requests


app = Flask(__name__)
app.config['SECRET_KEY'] = 'whatever'
api_bp = flask.Blueprint("api", __name__, url_prefix="/api")
api = Api(api_bp, title="Esports-info API", version="1.0", doc="/docs")
app.register_blueprint(api_bp)
twitch: Twitch
lq: Liquipedia
channel_api_model = api.model('Channel', {'channel': fields.String('Name of the channel')})


def get_team_info(name: str):
    info = []
    stream_title = stream_title = twitch.streams[name]['title']
    if not twitch.is_online(twitch.streams[name]) and twitch.active_video is not None:
        stream_title = twitch.active_video['title']
    for team_name in lq.team_names:
        if team_name.lower() in stream_title.lower() or team_name.replace(" ", "").lower() in stream_title.lower() \
                or team_name.lower().replace(" gaming", "") in stream_title.lower():
            info.append(team_name)
    return info


@api.route('/custom', endpoint='custom', methods=['POST', 'DELETE'])
class CreateCustomPageAPI(Resource):

    @api.expect(channel_api_model)
    def post(self):
        info = twitch.get_info_about(api.payload['channel'])['data']
        if len(info) > 0:
            if len(twitch.streams) < 5:
                twitch.add_stream(info[0]['display_name'])
                return make_response(
                    jsonify("Channel " + api.payload['channel'] + " was added between watched channels"), 200)
            else:
                return make_response(jsonify("Too many channels watched, please remove some"), 400)
        else:
            return make_response(jsonify("Channel " + api.payload['channel'] + " not found"), 404)

    @api.expect(channel_api_model)
    def delete(self):
        if api.payload['channel'] in twitch.streams:
            twitch.streams.pop(api.payload['channel'])
            return make_response(jsonify("Channel " + api.payload['channel'] + " was removed"), 200)
        return make_response(jsonify("Channel name " + api.payload['channel'] + " not found"), 404)


@api.route('/info/<string:name>', endpoint='info', methods=['GET'])
@api.doc(params={'name': 'Name of target twitch account.'})
class InfoAPI(Resource):
    def get(self, name):
        info = twitch.get_info_about(name)['data']
        if len(info) > 0:
            return info[0]
        else:
            return make_response(jsonify("Name " + name + " not found"), 404)


@app.route('/')
def index():
    twitch.refresh_streams()
    return render_template("index.html", streams=twitch.streams, stream_url=False, stream=False)


@app.route('/custom/<string:name>')
def custom(name: str):
    twitch.refresh_streams()
    stream_url = twitch.get_stream_url(name)
    teams = False
    if twitch.streams[name]['static']:
        teams = []
        for team in get_team_info(name):
            teams.append(lq.get_team_info(team))
        if len(teams) is 0:
            teams = False
    return render_template("custom.html", streams=twitch.streams, stream_url=stream_url, stream=name, teams=teams)


@app.route('/form/add', methods=['POST'])
def add_form():
    requests.post('http://127.0.0.1:5000/api/custom',
                  headers={'Content-Type': 'application/json', 'accept': 'application/json'},
                  data="{ \"channel\": \"" + request.form['channel'] + "\"}")
    return redirect('/')


@app.route('/form/delete', methods=['POST'])
def delete_form():
    requests.delete('http://127.0.0.1:5000/api/custom',
                    headers={'Content-Type': 'application/json', 'accept': 'application/json'},
                    data="{ \"channel\": \"" + request.form['channel'] + "\"}")
    return redirect('/')


if __name__ == "__main__":
    twitch = Twitch()
    twitch.add_stream_by_id("31239503")
    twitch.streams['ESL_CSGO']['static'] = True
    twitch.streams['ESL_CSGO']['display_name'] = "ESL"
    twitch.streams['ESL_CSGO']['banner'] = '/static/images/esl_logo.png'

    twitch.add_stream("dreamhackcs")
    twitch.streams['dreamhackcs']['static'] = True
    twitch.streams['dreamhackcs']['display_name'] = "Dreamhack"
    twitch.streams['dreamhackcs']['banner'] = '/static/images/dreamhack_logo.png'

    lq = Liquipedia()

    app.run(debug=True)
