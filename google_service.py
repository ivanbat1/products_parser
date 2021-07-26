from __future__ import print_function

import logging
import os.path
import io
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/drive']

logger = logging.getLogger("root")


class GoogleAPIServie:
    google_service = None

    def __init__(self, session):
        self.session = session

    def create(self):
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

    def get_image(self, image_id):
        request = self.google_service.files().get_media(fileId=image_id)
        image_data = self.google_service.files().get(fileId=image_id).execute()
        image_name = image_data["name"]
        fh = io.FileIO('images/' + image_name, mode='wb')
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            load_percents = int(status.progress() * 100)
            logger.info("Download {}%. {} {}".format(load_percents, image_id, image_name))
        return image_name
