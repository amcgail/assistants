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

except HttpError as e:
    print(f"Error: {e}")
    print("Please ensure that you have enabled the Google Calendar API for your project.")
    print("You can do so by visiting:")
    print("https://console.developers.google.com/apis/library/calendar-json.googleapis.com")
    print("and clicking 'Enable API'.")


class Search(Module):
  name = "calendar searcher"
  goal = "to search for events on Alec's calendar"
  params = """
    {
      "query": "search the title of the event (can use * as a wildcard)",
      "timeMin": "2023-11-20T00:00:00-05:00",
      "timeMax": "2023-11-20T23:59:59Z-05:00"
    }
  """

  detailed_instructions = flatten_whitespace("""
    Only give a query if you know exactly what you are looking for.
  """)         

  def execute_it(self, args):
    from itertools import groupby

    query = args['query'] if 'query' in args else '*'
    max_results = args.get('maxResults', 10)
    order_by = args.get('orderBy', 'startTime')
    single_events = args.get('singleEvents', True)
    time_min = args.get('timeMin', dt.datetime.utcnow().isoformat() + 'Z')
    time_max = args.get('timeMax', (dt.datetime.utcnow() + dt.timedelta(days=365)).isoformat() + 'Z')

    events = search_events(service, query, time_min, time_max)

    total_string = ''
    all_day_events = [x for x in events if 'date' in x['start']]
    timed_events = [x for x in events if 'dateTime' in x['start']]

    # sort the events by start time
    all_day_events = sorted(all_day_events, key=lambda x: x['start']['date'])
    timed_events = sorted(timed_events, key=lambda x: x['start']['dateTime'])

    def format_datetime(x):
        x = dt.datetime.fromisoformat(x)
        return x.strftime("%H:%M")
    
    total_string += "Timed Events Results:\n"
    for date, g in groupby(timed_events, key=lambda x: x['start']['dateTime'][:10]):
        day_of_week = dt.datetime.fromisoformat(date).strftime("%A")
        total_string += f"{date} ({day_of_week})"
        for event in g:
            total_string += f"\n  {format_datetime(event['start']['dateTime'])} - {format_datetime(event['end']['dateTime'])} - {event['summary']}"

    total_string += "\n\nAll Day Events Results:\n"
    for event in all_day_events:
        day_of_week = dt.datetime.fromisoformat(event['start']['date']).strftime("%A")
        day_of_week_end = dt.datetime.fromisoformat(event['end']['date']).strftime("%A")
        total_string += f"{event['start']['date']} ({day_of_week}) - {event['summary']}\n"

    return total_string

class NewEvent(Module):
  name = "event creator"
  goal = "to create a single new event on Alec's calendar."
  detailed_instructions = flatten_whitespace("""
    No need to invite Alec, you are creating events on his calendar.
    When scheduling, be careful not to conflict with pre-existing events!
    Check that there is no other prior event which conflicts with your new event.
  """)
  params = """
    {
      "summary": "short description of the event",
      "location": "location of the event",
      "description": "longer description of the event",
      "start": {
        "dateTime": "start time of the event",
        "timeZone": "America/New_York"
      },
      "end": {
        "dateTime": "end time of the event",
        "timeZone": "America/New_York"
      },
      "attendees": [] # never include attendees, please
    }
  """

  def execute_it(self, args):
    start_time = dt.datetime.fromisoformat(args['start']['dateTime'])
    end_time = dt.datetime.fromisoformat(args['end']['dateTime'])

    # add time-zone information
    tz1 = pytz.timezone(args['start']['timeZone'])
    tz2 = pytz.timezone(args['end']['timeZone'])

    # if the time zone is not specified, assume it is EST
    if start_time.tzinfo is None:
      start_time = tz1.localize(start_time)
    if end_time.tzinfo is None:
      end_time = tz2.localize(end_time)

    summary = args['summary']
    description = args['description']
    location = args['location']
    attendees = [attendee['email'] for attendee in args['attendees']]

    create_event(service, start_time, end_time, summary, description, location, attendees)
    return "Event created: {start_time:%m-%d %H:%M} {end_time:%m-%d %H:%M} {summary}".format(start_time=start_time, summary=summary, end_time=end_time)


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

    event = service.events().insert(calendarId='amcgail2@gmail.com', body=event).execute()
    print(f"Event created: {event.get('htmlLink')}")


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