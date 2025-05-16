import base64
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
import os
import re

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://mail.google.com/']

def create_message_rfc822(sender, to, subject, message_body):
    """Create a message in RFC822 format.

    Args:
        sender: The email address of the sender.
        to: The email address of the recipient.
        subject: The subject of the email message.
        message_body: The body of the email message.

    Returns:
        A string containing the message in RFC822 format.
    """
    message = f"From: {sender}\n"
    message += f"To: {to}\n"
    message += f"Subject: {subject}\n\n"
    message += message_body
    return message

def import_emails_from_file(filename):
    """Imports emails from a text file into Gmail using the Gmail API."""
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            print('Please authenticate your Gmail account. Run the quickstart.py from the Gmail API documentation first.')
            print('Make sure to authorize with the scope: https://mail.google.com/')

            # Note: For a script you intend to run without user interaction,
            # you would typically handle the authentication differently
            # (e.g., using a service account or a pre-authorized refresh token).
            # This simplified approach requires manual authorization.
            try:
                from google_auth_oauthlib.flow import InstalledAppFlow
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)  # Ensure you have credentials.json
                creds = flow.run_local_server(port=0)
                # Save the credentials for the next run
                with open('token.json', 'w') as token:
                    token.write(creds.to_json())
            except ImportError:
                print("Error: You need to install the google-auth-httplib2 and google-auth-oauthlib libraries.")
                print("Install them using: pip install --upgrade google-auth-httplib2 google-auth-oauthlib")
                return
            except FileNotFoundError:
                print("Error: The credentials.json file was not found. Make sure to download it from your Google Cloud Project.")
                return

    try:
        service = build('gmail', 'v1', credentials=creds)
        with open(filename, 'r') as f:
            email_content = f.read()
            email_blocks = re.split(r'--- EMAIL START ---\n', email_content)[1:] # Split and ignore the first empty part

            for block in email_blocks:
                if block.strip():
                    headers = {}
                    body_lines = []
                    in_body = False
                    for line in block.strip().split('\n'):
                        if not in_body and ':' in line:
                            key, value = line.split(':', 1)
                            headers[key.strip()] = value.strip()
                        else:
                            in_body = True
                            body_lines.append(line)

                    sender = headers.get('From')
                    to = headers.get('To')
                    subject = headers.get('Subject', '')
                    body = '\n'.join(body_lines).strip()

                    if sender and to:
                        raw_email_string = create_message_rfc822(sender, to, subject, body)
                        raw_email_bytes = raw_email_string.encode('utf-8')
                        raw_email_b64 = base64.urlsafe_b64encode(raw_email_bytes).decode('utf-8')

                        message = {'raw': raw_email_b64, 'labelIds': ['INBOX', 'UNREAD']}
                        imported_message = service.users().messages().import_(userId='me', body=message).execute()
                        print(f'Imported message with ID: {imported_message.get("id")}')
                    else:
                        print("Warning: Could not parse 'From' or 'To' address in an email block.")

    except Exception as error:
        print(f'An error occurred: {error}')

if __name__ == '__main__':
    filename = 'email_dataset.txt'
    import_emails_from_file(filename)