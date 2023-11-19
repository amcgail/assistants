from ..common import *

import datetime as dt

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from pathlib import Path

import pytz


# Define the EST timezone
est = pytz.timezone('America/New_York')

# If modifying these scopes, delete the file token.json.
SCOPES = [
  "https://www.googleapis.com/auth/calendar.readonly",
  "https://www.googleapis.com/auth/calendar",
]

cred_folder = Path(__file__).parent.parent / '.creds'
cred_file = cred_folder / 'gcalendar.json'
token_file = cred_folder / 'gcalendar_token.json'


def search_events(service, query, time_min, time_max, calendar_id='amcgail2@gmail.com'):
    events_result = service.events().list(
        calendarId=calendar_id,
        q=query,  # Search keyword
        timeMin=time_min,
        timeMax=time_max,
        singleEvents=True,
        orderBy='startTime'
    ).execute()

    return events_result.get('items', [])


"""Shows basic usage of the Google Calendar API.
Prints the start and name of the next 10 events on the user's calendar.
"""
creds = None
# The file token.json stores the user's access and refresh tokens, and is
# created automatically when the authorization flow completes for the first
# time.
if token_file.exists():
    creds = Credentials.from_authorized_user_file(str(token_file), SCOPES)
# If there are no (valid) credentials available, let the user log in.
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            cred_file, SCOPES
        )
        creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with token_file.open("w") as token:
        token.write(creds.to_json())

try:
    service = build("calendar", "v3", credentials=creds)

    events = search_events(service, "diss", "2022-01-01T00:00:00Z", "2023-12-31T23:59:59Z")

    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        print(start, event['summary'])

except HttpError as e:
    print(f"Error: {e}")
    print("Please ensure that you have enabled the Google Calendar API for your project.")
    print("You can do so by visiting:")
    print("https://console.developers.google.com/apis/library/calendar-json.googleapis.com")
    print("and clicking 'Enable API'.")