from os import environ
from concurrent.futures import ThreadPoolExecutor
from uuid import uuid4
from flask import *
from werkzeug.exceptions import InternalServerError
from requests import post

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build

from gradesync import *


CLIENT_SECRETS_FILE = 'credentials.json'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly', 'https://www.googleapis.com/auth/classroom.coursework.students', 'https://www.googleapis.com/auth/classroom.courses.readonly', 'https://www.googleapis.com/auth/classroom.rosters.readonly', 'https://www.googleapis.com/auth/classroom.profile.emails']

app = Flask(__name__)
app.secret_key = environ['FLASK_SECRET']

executor = ThreadPoolExecutor()
jobs = {}


@app.route('/', methods=['GET'])
def index():
    if 'credentials' not in session:
        return redirect('authorize')
    credentials = Credentials(**session['credentials'])
    classroom = build('classroom', 'v1', credentials=credentials)
    session['credentials'] = credentials_to_dict(credentials)
    return render_template('index.html', courses=get_courses(classroom), fields=CONFIG_FIELDS)


@app.route('/start', methods=['POST'])
def start():
    if 'job' in session:
        return jsonify({}), 429
    if 'credentials' not in session:
        return jsonify({}), 401
    credentials = Credentials(**session['credentials'])
    sheets = build('sheets', 'v4', credentials=credentials)
    classroom = build('classroom', 'v1', credentials=credentials)
    session['credentials'] = credentials_to_dict(credentials)
    session['job'] = uuid4().hex
    jobs[session['job']] = executor.submit(sync, sheets=sheets, classroom=classroom, config=request.form)
    return 'Syncing started!', 202


@app.route('/poll', methods=['GET'])
def poll():
    if 'job' not in session:
        return jsonify({}), 404
    job = jobs.pop(session['job'])
    if job.done():
        del session['job']
        return jsonify(job.result())
    jobs[session['job']] = job
    return jsonify({}), 423


@app.route('/authorize')
def authorize():
    flow = Flow.from_client_secrets_file(CLIENT_SECRETS_FILE, scopes=SCOPES)
    flow.redirect_uri = url_for('oauth2callback', _external=True)
    authorization_url, state = flow.authorization_url(access_type='offline')
    session['state'] = state
    return redirect(authorization_url)


@app.route('/oauth2callback')
def oauth2callback():
    state = session['state']
    flow = Flow.from_client_secrets_file(CLIENT_SECRETS_FILE, scopes=SCOPES, state=state)
    flow.redirect_uri = url_for('oauth2callback', _external=True)
    authorization_response = request.url
    flow.fetch_token(authorization_response=authorization_response)
    credentials = flow.credentials
    session['credentials'] = credentials_to_dict(credentials)
    return redirect(url_for('index'))


@app.errorhandler(InternalServerError)
def handle_500(e):
    if 'job' in session:
        job = jobs.pop(session['job'], None)
        if job: job.cancel()
        del session['job']
    if 'credentials' in session:
        credentials = Credentials(**session['credentials'])
        del session['credentials']
        revoke = post('https://accounts.google.com/o/oauth2/revoke',
                      params={'token': credentials.token},
                      headers={'content-type': 'application/x-www-form-urlencoded'})
    return 'Token revoked!', 400


def credentials_to_dict(credentials):
    return {'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes}


if __name__ == '__main__':
    app.run()
