from pathlib import Path
import flask
from flask import Flask, render_template, make_response, jsonify, redirect, url_for, request
from flask_restplus import Api, Resource
from twitch import Twitch
import requests

app = Flask(__name__)
api_bp = flask.Blueprint("api", __name__, url_prefix="/api")
api = Api(api_bp, title="Esports-info API", version="1.0", doc="/docs")
app.register_blueprint(api_bp)

twitch: Twitch


@api.route('/info/<string:name>', endpoint='info', methods=['GET'])
@api.doc(params={'name': 'Name of target twitch account.'})
class InfoAPI(Resource):
    def get(self, name):
        info = twitch.get_info_about(name)['data']
        if len(info) > 0:
            return info[0]
        else:
            return make_response(jsonify("Name " + name + " not found"), 404)


@api.route('/custom', endpoint='custom', methods=['GET', 'POST', 'DELETE'])
class CreateCustomPageAPI(Resource):
    def get(self):
        return redirect(url_for('index'))

    def post(self):
        info = twitch.get_info_about(request.form['channel'])['data']
        if len(info) > 0:
            twitch.add_stream(info[0]['display_name'])
            return redirect(url_for('custom', name=info[0]['display_name']))
        else:
            return make_response(jsonify("Name " + request.form['channel'] + " not found"), 404)

    def delete(self):
        if request.form['channel'] in twitch.streams:
            twitch.streams.pop(request.form['channel'])
        return redirect(url_for('index'))


@app.route('/')
def index():
    twitch.refresh_streams()
    return render_template("index.html", streams=twitch.streams, stream_url=False, stream=False)


@app.route('/custom/<string:name>')
def custom(name: str):
    twitch.refresh_streams()
    return render_template("custom.html", streams=twitch.streams, stream_url=twitch.get_stream_url(name), stream=name)


if __name__ == "__main__":
    twitch = Twitch()
    twitch.add_stream("esl_csgo")
    twitch.streams['esl_csgo']['static'] = True
    twitch.streams['esl_csgo']['display_name'] = "ESL"
    twitch.streams['esl_csgo']['banner'] = '/static/images/esl_logo.png'

    twitch.add_stream("dreamleague")
    twitch.streams['dreamleague']['static'] = True
    twitch.streams['dreamleague']['display_name'] = "Dreamhack"
    twitch.streams['dreamleague']['banner'] = '/static/images/dreamhack_logo.png'
    app.run(debug=True)
