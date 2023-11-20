from ..common import *
from . import Module

import datetime as dt

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from pathlib import Path

import pytz


class NewEvent(Module):
  params = """
    {
      'summary': 'short description of the event',
      'location': 'location of the event',
      'description': 'longer description of the event',
      'start': {
        'dateTime': 'start time of the event',
        'timeZone': 'timezone of the event',
      },
      'end': {
        'dateTime': 'end time of the event',
        'timeZone': 'timezone of the event',
      },
      'attendees': [
        {'email': 'email of attendee 1'},
        {'email': 'email of attendee 2'},
        ...
      ]
    }
  """

  actions = {
    "clarify": "Send an email to Alec asking for clarification about the event.",
  }

  def get_prompt(self, query):
    return flatten_whitespace(f"""
      Your goal is to create a new event on your calendar. Invite amcgail2@gmail.com.
      The structure of your response should be as follows:
      {self.params}
      Query:
      {query}
    """)



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

import os.path

def list_all_calendars(service):
    calendars = service.calendarList().list().execute()
    return [calendar['id'] for calendar in calendars['items']]

# Add this function to create an event
def create_event(service, start_time, end_time, summary, description, location, attendees):
    assert type(start_time) == dt.datetime
    assert type(end_time) == dt.datetime
    start_timezone = start_time.strftime('%Z')
    end_timezone = start_time.strftime('%Z')

    event = {
        'summary': summary,
        'location': location,
        'description': description,
        'start': {
            'dateTime': start_time.isoformat(),
            'timeZone': start_timezone,
        },
        'end': {
            'dateTime': end_time.isoformat(),
            'timeZone': end_timezone,
        },
        'attendees': [{'email': attendee} for attendee in attendees],
        'reminders': {
            'useDefault': False,
            'overrides': [
                {'method': 'email', 'minutes': 24 * 60},
                {'method': 'popup', 'minutes': 10},
            ],
        },
    }

    event = service.events().insert(calendarId='primary', body=event).execute()
    print(f"Event created: {event.get('htmlLink')}")


def main():
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

    # Call the Calendar API
    now = dt.datetime.utcnow()
    
    # add timezone information
    now = now.isoformat() + "Z"  # 'Z' indicates UTC time

    print("Getting the upcoming 10 events")
    events_result = (
        service.events()
        .list(
            calendarId="amcgail2@gmail.com",
            timeMin=now,
            maxResults=10,
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )
    events = events_result.get("items", [])

    if not events:
      print("No upcoming events found.")
      return

    # Example data for a new event, modify as needed
    # make sure there are timezones
    start_time = dt.datetime.now(est) + dt.timedelta(days=1)
    end_time = start_time + dt.timedelta(hours=2)

    summary = "New Event"
    description = "Description of the event"
    location = "Location of the event"
    attendees = ["am2873@cornell.edu"]

    # Call the function to create an event
    create_event(service, start_time, end_time, summary, description, location, attendees)

  except HttpError as error:
    print(f"An error occurred: {error}")

  
if __name__ == "__main__":
  main()