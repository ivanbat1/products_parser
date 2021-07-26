from __future__ import print_function
import requests
import io
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.http import MediaIoBaseDownload

from constants import API_KEY, URL_NAME, AUTH

SCOPES = ['https://www.googleapis.com/auth/drive']


class ParserGoogleDriveFile:

    drive_service = None
    image_sizes = "800x800"
    image_url = URL_NAME + '/api/0/images'
    path_to_image = 'images/{}.png'

    def __init__(self, session):
        self.session = session

    def create_google_service(self):
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

        self.drive_service = build('drive', 'v3', credentials=creds, developerKey=API_KEY)

    def get_image_from_google(self, id_google_file, title):
        request = self.drive_service.files().get_media(fileId=id_google_file)

        path_to_image = self.path_to_image.format(title)
        fh = io.FileIO(path_to_image, mode='wb')
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            print("Download %d%%." % int(status.progress() * 100))

    def load_image_to_catalog(self, title):
        path_to_image = self.path_to_image.format(title)
        print(path_to_image)
        json_data = {
                'title': title,
                'sizes': self.image_sizes
            }
        req = self.session.post(
            self.image_url,
            json=json_data,
            files={"image": open(path_to_image, 'rb')}
        )
        print(req.json())
        catalog_path_to_image = req.json().get('data', {}).get('uri', '')
        return catalog_path_to_image