import googleapiclient
import requests
from constants import URL_NAME, AUTH
from google_api_connect import ParserGoogleDriveFile


class Parser:

    json_data = {}
    json_access = {}
    code_by_id = {}

    def __init__(self, ws):
        self.ws = ws
        self.session = requests.Session()
        self.session.auth = AUTH
        self.Parser_Google_Drive_File = ParserGoogleDriveFile(self.session)
        self.Parser_Google_Drive_File.create_google_service()

    def get_key(self, cell):
        col = cell.col_idx
        key = self.ws.cell(1, col).value
        return key.strip()

    def get_method_by_key(self, key):
        if key is None:
            return
        elif "image" in key:
            return self.parse_image
        elif "access" in key:
            return self.access
        elif key == "relatedProfile":
            return self.related_profile
        elif "alternativeNames" in key:
            return self.alternative_names
        elif "additionalProperties" in key or "additionalClassifications" in key or "alternativeIdentifiers" in key:
            return self.additional_properties
        elif key[0].isdigit():
            return self.requirement_responses
        else:
            return self.parse_key

    def parse_image(self, key, value):
        id_google_file = value.split("id=")[-1]
        print(id_google_file)
        try:
            self.Parser_Google_Drive_File.get_image_from_google(id_google_file, 'image_1010')
        except googleapiclient.errors.HttpError as error:
            print(error)
            return
        catalog_path_to_image = self.Parser_Google_Drive_File.load_image_to_catalog('image_1010')
        self.json_data.setdefault("images", [])
        self.json_data["images"].append({
            'sizes': '800x800',
            'url': catalog_path_to_image
        })

    def requirement_responses(self, key, value):
        self.json_data.setdefault("requirementResponses", [])
        self.json_data["requirementResponses"].append({
            "requirement": key,
            "value": value,
            "id": self.code_by_id.get(key)
        })

    def additional_properties(self, key, value):
        head_key, second_key = key.strip().split(":")
        self.json_data.setdefault(head_key, [])
        properties = self.json_data[head_key]
        if not properties:
            properties.append({second_key: value})
        for data in properties:
            if len(data) <= 3:
                data.update({second_key: value})
            else:
                properties.append({second_key: value})

    def alternative_names(self, key, value):
        head_key, second_key = key.strip().split(":")
        self.json_data.setdefault(head_key, {}).setdefault(second_key, [])
        self.json_data[head_key][second_key].append(value)

    def parse_key(self, key, value):
        key = key.strip()
        if ":" in key:
            head_key, second_key = key.split(":")
            self.json_data.setdefault(head_key, {})
            self.json_data[head_key][second_key] = str(value)
        else:
            self.json_data.setdefault(key, value)

    def related_profile(self, key, value):
        url = URL_NAME + "/api/0/profiles/{profile_id}".format(profile_id=value)
        response = self.session.get(url)
        if response.status_code != 200:
            print("profile status_code = {}".format(response.status_code))
            return
        json_response = response.json()
        criteries = json_response.get("data", {}).get("criteria", [])
        for criteria in criteries:
            criteria_code = criteria.get('code')[5:]
            for requirement_group in criteria.get("requirementGroups"):
                for requirement in requirement_group.get("requirements"):
                    requirement_id = requirement.get('id')
                    self.code_by_id[requirement_id] = criteria_code
        self.json_data.setdefault(key, value)

    def access(self, key, value):
        _, second_key = key.split(":")
        self.json_access.setdefault(second_key, str(value))
