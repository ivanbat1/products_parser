VERSION_API = "VERION API"
URL_NAME = "URL TO CATALOG"
XLSX_FILE_NAME = "FILE NAME"
SHEET_NAME = "SHEET NAME"
AUTH = ('LOGIN', 'PASS')
API_KEY = "YOUR API KEY"
IMAGES_FILE_PATH = 'PATH TO IMAGE FILE'
DEBUG = True  # for developers

try:
    from local_constants import *
except ImportError:
    pass