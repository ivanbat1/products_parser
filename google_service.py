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
    google_service = None
    sizes = '800x800'

    def __init__(self, session):
        self.session = session

    def main(self):
        creds = None
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            with open('token.json', 'w') as token:
                token.write(creds.to_json())

        self.google_service = build('drive', 'v3', credentials=creds)

    def get_file(self, file_id):
        request = self.google_service.files().get_media(fileId=file_id)
        file = self.google_service.files().get(fileId=file_id).execute()
        title = file["name"]
        fh = io.FileIO('images/' + title, mode='wb')
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            load_percents = int(status.progress() * 100)
            print ("Download {}%. {} {}".format(load_percents, file_id, title))
        return title

    def load_file_to_catalog(self, title):
        url = URL_NAME + '/api/0/images'
        json_data = {
            "title": title,
            "sizes": self.sizes,
        }
        print(json_data)
        req = self.session.post(url,
                                data=json_data,
                                files={"image": open('images/' + title, 'rb')})
        if req.status_code == 201:
            local_catalog_image_url = req.json().get('data', {}).get('uri')
            print(req.json())
            return local_catalog_image_url
        else:
            print(req.content)
            return