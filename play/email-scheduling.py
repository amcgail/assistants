# the goal here is to have the assistant schedule a meeting with someone

target_name = "Patrick McGail"
target_email = "am2873@cornell.edu"
target_dates = "within one week"

import datetime as dt
todays_date = dt.datetime.today().strftime('%Y-%m-%d')
current_time = dt.datetime.now().strftime("%H:%M:%S")

# we should basically make a pipeline

# CLARIFICATION STEPS
# step 1. clarify with Alec the purpose, target(s), and deadline of the meeting.
# step 2. if possible, research the target(s) and find their email address(es), and any other relevant information about them
# step 3. [optional, depends] once clarified, draft an introduction email and send to Alec for approval

# CONTACT STEPS
# step 1b. initiate conversation, clearly stating the purpose of the meeting

# step 2. wait for response. if no response in deadline/4 days, send a reminder
# step 2a. if no response in deadline/2 days, send a reminder
# step 2b. if no response in deadline, cancel task and email Alec

# step 3. if response, correspond with the person to schedule a meeting, clarifying when they can and cannot meet
# step 4. once everything is clarified, send a calendar invite to the person and Alec


prompt = f"""
Please only provide a body, no subject.
Sign the email as "Alec's AI Assistant".
You are Alec McGail's assistant.
"""