import logging
import requests
from constants import URL_NAME, AUTH, IMAGES_FILE_PATH
from google_service import GoogleAPIService
from werkzeug.utils import secure_filename


logger = logging.getLogger("root")


class Parser:
    json_data = {}
    json_access = {}
    requirement_responses_code_by_requirement = {}
    sizes = "800x800"
    url_profiles = URL_NAME + "profiles/{profile_id}"
    url_images = URL_NAME + "images"

    def __init__(self, ws):
        self.ws = ws
        self.session = requests.Session()
        self.session.auth = AUTH
        self.google_service = GoogleAPIService(self.session)
        self.google_service.create()

    def get_key(self, cell):
        col = cell.col_idx
        key = self.ws.cell(1, col).value
        return key.strip()

    def split_key(self, key):
        return key.split(":")

    def get_method_by_key(self, key):
        if key is None:
            return
        elif "image" in key:
            return self.parse_image_from_google_drive
        elif "access" in key:
            return self.parse_access
        elif key == "relatedProfile":
            return self.parse_related_profile
        elif "alternativeNames" in key:
            return self.parse_alternative_names
        elif "additionalProperties" in key or "additionalClassifications" in key or "alternativeIdentifiers" in key:
            return self.parse_additional_properties
        elif key[0].isdigit():
            return self.parse_requirement_responses
        else:
            return self.parse_key_without_specifics

    def load_image_to_catalog(self, image_name):
        title = image_name.split(".")[0]
        url = self.url_images
        image_data = {
            "title": title,
            "sizes": self.sizes,
        }
        logger.info(image_data)
        image_type = image_name.split(".")[-1]
        mime_type = f'image/{image_type}'
        image_tuple = (image_name,
                       open(IMAGES_FILE_PATH + image_name, 'rb').read(),
                       mime_type)
        response = self.session.post(url,
                                     data=image_data,
                                     files={"image": image_tuple}
                                     )
        if response.status_code == 201:
            local_catalog_image_url = response.json().get('data', {}).get('url')
            logger.info(response.json())
            return local_catalog_image_url
        elif "Image already exists" in response.json().get("error", {}).get("message", ""):
            filename = secure_filename(image_name).lower()
            image_id = filename.replace('.', '_')
            url_get_image = "{}/{}".format(self.url_images, image_id)
            response = self.session.get(url_get_image)
            local_catalog_image_url = response.json().get('data', {}).get('url')
            logger.info(response.json())
            return local_catalog_image_url
        else:
            logger.info(response.content)
            return

    def parse_image_from_google_drive(self, key, value):
        if "drive.google.com" in value:
            image_id = value.split('id=')[-1]
            try:
                image_name = self.google_service.get_image(image_id)
            except Exception as ex:
                logger.error(ex)
                return
            catalog_image_path = self.load_image_to_catalog(image_name)
        else:
            catalog_image_path = value

        if catalog_image_path is None:
            return

        self.json_data.setdefault("images", [])
        image_data = {
            "url": catalog_image_path,
            "sizes": self.sizes
        }
        self.json_data["images"].append(image_data)

    def parse_requirement_responses(self, key, value):
        self.json_data.setdefault("requirementResponses", [])
        self.json_data["requirementResponses"].append({
            "requirement": key,
            "value": value,
            "id": self.requirement_responses_code_by_requirement.get(key)
        })

    def parse_additional_properties(self, key, value):
        head_key, second_key = self.split_key(key)
        self.json_data.setdefault(head_key, [])
        properties = self.json_data[head_key]
        if not properties:
            properties.append({second_key: value})
        for data in properties:
            if len(data) <= 3:
                data.update({second_key: value})
            else:
                properties.append({second_key: value})

    def parse_alternative_names(self, key, value):
        head_key, second_key = self.split_key(key)
        self.json_data.setdefault(head_key, {}).setdefault(second_key, [])
        self.json_data[head_key][second_key].append(value)

    def parse_key_without_specifics(self, key, value):
        if ":" in key:
            head_key, second_key = self.split_key(key)
            self.json_data.setdefault(head_key, {})
            self.json_data[head_key][second_key] = str(value)
        else:
            self.json_data.setdefault(key, value)

    def parse_related_profile(self, key, value):
        url = self.url_profiles.format(profile_id=value)
        response = self.session.get(url)
        if response.status_code != 200:
            logger.info("profile {} status_code = {}".format(url, response.status_code))
            return
        json_response = response.json()
        criteries = json_response.get("data", {}).get("criteria", [])
        for criteria in criteries:
            criteria_code = criteria.get('code')[5:]
            for requirement_group in criteria.get("requirementGroups"):
                for requirement in requirement_group.get("requirements"):
                    requirement_id = requirement.get('id')
                    self.requirement_responses_code_by_requirement[requirement_id] = criteria_code
        self.json_data.setdefault(key, value)

    def parse_access(self, key, value):
        _, second_key = self.split_key(key)
        self.json_access.setdefault(second_key, str(value))
