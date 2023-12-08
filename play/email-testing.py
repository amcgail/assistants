from ..modules.emailer import *

# Process received email and respond
sender, subject, body = receive_email()

prompt = f"""
Respond to the following email.
Please only provide a body, no subject.
Sign the email as "Alec's AI Assistant".
You are Alec McGail's assistant.

Subject:\n{subject}\n
Body:\n{body}
"""

response = client.chat.completions.create(
    model = "gpt-3.5-turbo",
    messages = [{
        "role": "system",
        "content": prompt
    }]
)

response = response.choices[0].message.content

send_email(sender, f"Re: {subject}", response)
