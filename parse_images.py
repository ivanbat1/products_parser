import logging
import requests
from constants import IMAGES_FILE_PATH, AUTH, URL_NAME
from werkzeug.utils import secure_filename
from PIL import Image as PILImage


logger = logging.getLogger("root")


class ParserImage:

    @staticmethod
    def get_image_sizes(image_name):
        path_to_local_image = IMAGES_FILE_PATH + image_name
        im = PILImage.open(path_to_local_image)
        width, height = im.size
        return "{}x{}".format(width, height)

    @staticmethod
    def get_image(url_image):
        image_name = url_image.split("/")[-1]

        r = requests.get(url_image, stream=True)
        if r.status_code == 200:
            r.raw.decode_content = True
            with open(IMAGES_FILE_PATH + image_name, 'wb') as f:
                f.write(r.content)
            logger.info('Image sucessfully Downloaded: {}'.format(image_name))
            print('Image sucessfully Downloaded: ', image_name)
            return image_name
        else:
            logger.info('Image Couldn\'t be retreived')
            print('Image Couldn\'t be retreived')
            return


class Image(ParserImage):
    url_catalog_api_images = URL_NAME + "images"
    res_image_data = {}

    def __init__(self, url_image, session, google_service):
        self.session = session
        self.url_image_from_file = url_image
        self.google_service = google_service

    def get_catalog_image_data(self):
        if "drive.google.com" in self.url_image_from_file:
            logger.info('image from googledrive')
            image_id = self.url_image_from_file.split('id=')[-1]
            try:
                image_name = self.google_service.get_image(image_id)
            except Exception as ex:
                logger.error(ex)
                return
        else:
            image_name = self.get_image(self.url_image_from_file)
        if image_name is None:
            return

        self.load_image_to_catalog(image_name)
        catalog_image_url = self.res_image_data.get('url')
        catalog_image_sizes = self.res_image_data.get('sizes')
        return [catalog_image_url, catalog_image_sizes]

    def load_image_to_catalog(self, image_name):
        image_title = image_name.split(".")[0]
        image_sizes = self.get_image_sizes(image_name)
        image_data = {
            "title": image_title,
            "sizes": image_sizes,
        }
        logger.info(image_data)
        image_type = image_name.split(".")[-1]
        mime_type = f'image/{image_type}'
        image_tuple = (image_name,
                       open(IMAGES_FILE_PATH + image_name, 'rb').read(),
                       mime_type)
        response = self.session.post(self.url_catalog_api_images,
                                     data=image_data,
                                     files={"image": image_tuple}
                                     )
        if response.status_code == 201:
            self.res_image_data = response.json().get('data', {})
            logger.info(response.json())
        elif "Image already exists" in response.json().get("error", {}).get("message", ""):
            filename = secure_filename(image_name).lower()
            image_id = filename.replace('.', '_')
            url_get_image = "{}/{}".format(self.url_catalog_api_images, image_id)
            response = self.session.get(url_get_image)
            self.res_image_data = response.json().get('data', {})
            logger.info(response.json())
        else:
            self.res_image_data = {}
            logger.info(response.content)
            return
