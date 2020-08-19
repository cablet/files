from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import base64
from email.mime.text import MIMEText
from apiclient import errors

pickle_path = os.path.dirname(os.path.abspath(__file__)) + '/token.pickle'

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.send',
          'https://www.googleapis.com/auth/gmail.compose',
          'https://www.googleapis.com/auth/gmail.labels']

class Gmail():

    def __init__(self, cred_file, sender, to, subject, message_text):
        """Initialize gmail email
        """
        creds = None
        if os.path.exists(cred_file):

            # The file token.pickle stores the user's access and refresh tokens, and is
            # created automatically when the authorization flow completes for the first
            # time.
            if os.path.exists(pickle_path):
                with open(pickle_path, 'rb') as token:
                    print("token.pickle path already exists.")
                    creds = pickle.load(token)
            # If there are no (valid) credentials available, let the user log in.
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    print("Refreshing token.pickle.")
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        cred_file, SCOPES)
                    creds = flow.run_local_server(port=0)
                # Save the credentials for the next run
                with open(pickle_path, 'wb') as token:
                    pickle.dump(creds, token)

            self.service = build('gmail', 'v1', credentials=creds)
            if not self.service:
                print("Gmail: Error creating service")


            email = self.create_message(sender, to, subject, message_text)

            self.message = self.send_message(self.service, sender, email)
        else:
            print("Gmail credentials file not found at: {}".format(cred_file))



    def create_message(self, sender, to, subject, message_text):
            """Create a message for an email.

            Args:
              sender: Email address of the sender.
              to: Email address of the receiver.
              subject: The subject of the email message.
              message_text: The text of the email message.

            Returns:
              An object containing a base64url encoded email object.
            """
            message = MIMEText(message_text)
            message['to'] = to
            message['from'] = sender
            message['subject'] = subject
            # return {'raw': base64.urlsafe_b64encode(message.as_string())}
            return {'raw': base64.urlsafe_b64encode(message.as_string().encode()).decode()}

    def send_message(self, service, user_id, message):
          """Send an email message.

          Args:
            service: Authorized Gmail API service instance.
            user_id: User's email address. The special value "me"
            can be used to indicate the authenticated user.
            message: Message to be sent.

          Returns:
            Sent Message.
          """
          try:
            message = (service.users().messages().send(userId=user_id, body=message)
                       .execute())
            print('Message Id: %s' % message['id'])
            return message
          except errors.HttpError as error:
            print('An HTTP Error occurred: %s' % error)

    def message(self):
        return self.message



