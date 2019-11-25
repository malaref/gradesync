from __future__ import print_function
from re import match
from pickle import load, dump
from os.path import exists
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from gradesync import *

SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly', 'https://www.googleapis.com/auth/classroom.coursework.students', 'https://www.googleapis.com/auth/classroom.courses.readonly', 'https://www.googleapis.com/auth/classroom.rosters.readonly', 'https://www.googleapis.com/auth/classroom.profile.emails']
TOKEN_FILE = 'token.pickle'
creds = None
if exists(TOKEN_FILE):
    with open(TOKEN_FILE, 'rb') as token:
        creds = load(token)
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            'credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open(TOKEN_FILE, 'wb') as token:
        dump(creds, token)

sheets = build('sheets', 'v4', credentials=creds)
classroom = build('classroom', 'v1', credentials=creds)


courses = get_courses(classroom)
for idx, course in enumerate(courses):
    print(f"{idx}: {course['name']}")
idx = int(input(f"Choose course [{1} - {len(courses)}]: "))

config = {'course_id': courses[idx]['id']}

for field in CONFIG_FIELDS:
    value = input(f"{field['label']}: ")
    config[field['name']] = value


warnings = sync(sheets, classroom, config)
if warnings:
    print('Done with the following warning(s)!')
    for warning in warnings:
        print(warning)
else:
    print('Done!')
