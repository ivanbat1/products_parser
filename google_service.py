from __future__ import print_function
import os.path
import io
import requests
from constants import URL_NAME, AUTH
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/drive']

class GoogleAPIServie:
    service = None
    sizes = '800x800'

    def __init__(self, session):
        self.session = session

    def main(self):
        """Shows basic usage of the Drive v3 API.
        Prints the names and ids of the first 10 files the user has access to.
        """
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
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(creds.to_json())

        self.service = build('drive', 'v3', credentials=creds)

    def get_file(self, file_id, title):
        request = self.service.files().get_media(fileId=file_id)
        fh = io.FileIO('images/' + title + '.png', mode='w+')
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            print ("Download %d%%." % int(status.progress() * 100))

    def load_file_to_catalog(self, title):
        url = URL_NAME + '/api/0/images'
        json_data = {
            'title': title,
            'sizes': self.sizes
        }
        req = self.session.post(url,
                                data=json_data,
                                files={'image': open('images/' + title + '.png', 'rb')})
        if req.status_code == 201:
            local_catalog_image_url = req.json().get('data', {}).get('uri')
            print(req.json())
            return local_catalog_image_url
        else:
            print(req.text)
            return

#if __name__ == '__main__':
#    session = requests.Session()
#    session.auth = AUTH
#    service = GoogleAPIServie(session)
#    service.main()
#    service.get_file('1Ysq9jKaOj8Mi87YYDe2_Ujzw86ht5cRV', 'Ivan_test')
#    service.load_file_to_catalog('Ivan_test')