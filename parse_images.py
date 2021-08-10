import logging
import requests
from constants import IMAGES_FILE_PATH, AUTH, URL_NAME
from werkzeug.utils import secure_filename
from google_service import GoogleAPIService

logger = logging.getLogger("root")


class ParserImage:
    url_images = URL_NAME + "images"
    sizes = "800x800"

    def __init__(self, url):
        self.session = requests.Session()
        self.session.auth = AUTH
        self.google_service = GoogleAPIService(self.session)
        self.google_service.create()
        self.url = url

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

    def parse_image(self, image_url):
        filename = image_url.split("/")[-1]

        r = requests.get(image_url, stream=True)
        if r.status_code == 200:
            r.raw.decode_content = True
            with open(IMAGES_FILE_PATH + filename, 'wb') as f:
                f.write(r.content)
            logger.info('Image sucessfully Downloaded: {}'.format(filename))
            print('Image sucessfully Downloaded: ', filename)
            return filename
        else:
            logger.info('Image Couldn\'t be retreived')
            print('Image Couldn\'t be retreived')
            return

    def get_catalog_image_path(self):
        if "drive.google.com" in self.url:
            image_id = self.url.split('id=')[-1]
            try:
                image_name = self.google_service.get_image(image_id)
            except Exception as ex:
                logger.error(ex)
                return
        else:
            image_name = self.parse_image(self.url)
        if image_name is None:
            return

        catalog_image_path = self.load_image_to_catalog(image_name)

        return catalog_image_path
