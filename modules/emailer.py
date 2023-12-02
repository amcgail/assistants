from modularity import *

class SendEmail(Module):
    goal = "to send an email"
    name = "emailer"
    detailed_instructions = flatten_whitespace("""
    You will need to provide an exact email address.
    If you don't know the email address, add Alec to the recipients and note in the message that Alec needs to forward the email.
    Please only provide a body, no subject.
    Sign the email as "Alec's AI Assistant".
                                               
    Only send emails to the following addresses:
    - Mom: bajap123@gmail.com
    - Dad: bajap21@gmail.com
    - Alec: amcgail2@gmail.com
    """)
    params = """
        {
            'recipients': ['email address 1', 'email address 2'],
            'subject': 'subject of the email',
            'message': 'body of the email'
        }
    """

    def execute_it(self, args):
        send_email(args['recipients'], args['subject'], args['message'])
        return "Email sent."

import smtplib
import imaplib
import email
from email.mime.text import MIMEText

my_email = os.environ.get('EMAIL_ADDRESS')
my_password = os.environ.get('EMAIL_PASSWORD')

def get_email_content(email_message):
    # Assuming email_message is an email.message.EmailMessage object
    if email_message.is_multipart():
        for part in email_message.walk():
            # Check the content type of the part
            if part.get_content_type() == 'text/plain':
                # Extract and decode the content
                body = part.get_payload(decode=True)
                # Convert bytes to string if necessary
                body = body.decode(part.get_content_charset() or 'utf-8')
                return body
    else:
        # For non-multipart emails, just get the payload
        body = email_message.get_payload(decode=True)
        # Convert bytes to string if necessary
        body = body.decode(email_message.get_content_charset() or 'utf-8')
        return body


# Email sending function
def send_email(recipients, subject, message):
    sender = my_email
    password = my_password

    msg = MIMEText(message)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = ', '.join(recipients)

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(sender, password)
    server.sendmail(sender, recipients, msg.as_string())
    server.quit()

# Email receiving function
def receive_email():
    server = imaplib.IMAP4_SSL('imap.gmail.com', 993)
    server.login(my_email, my_password)
    server.select('inbox')

    _, data = server.search(None, 'ALL')
    mail_ids = data[0].split()
    print(len(mail_ids), 'emails found')
    latest_email_id = mail_ids[-1]
    print(latest_email_id)

    _, data = server.fetch(latest_email_id, '(RFC822)')
    raw_email = data[0][1].decode("utf-8")
    print(raw_email)
    
    email_message = email.message_from_string(raw_email)
    server.logout()

    # Extract subject and body from the email
    subject = email_message['subject']
    body = get_email_content(email_message)

    print(subject, body)

    sender = email.utils.parseaddr(email_message['from'])[1]

    return sender, subject, body