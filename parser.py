import json

import requests
from openpyxl import load_workbook
from constants import URL_NAME, XLSX_FILE_NAME, AUTH, DEBUG
from framework import Parser
import logging.config

if DEBUG:
    LOGGING_CONFIG = json.load(open('log_config.json', 'r'))
    logging.config.dictConfig(LOGGING_CONFIG)

logger = logging.getLogger("root")


class Products:
    products_data = []
    products_url = URL_NAME + "products/{product_id}"
    
    def __init__(self, ws):
        self.ws = ws
        self.parser = Parser(ws)
        self.session = requests.Session()
        self.session.auth = AUTH

    def parse_file(self):
        for row in list(self.ws.rows)[1:]:
            self.parser.json_data = {"status": "active"}
            self.parser.json_access = {}
            for cell in row:
                value = cell.value
                if value is None:
                    continue
                key = self.parser.get_key(cell)
                if value == "true":
                    value = True
                elif value == "false":
                    value = False
                method = self.parser.get_method_by_key(key)
                if method:
                    method(key, value)
            data = {
                "access": self.parser.json_access,
                "data": self.parser.json_data
            }
            log = 'parse {}'.format(data.get("data", {}).get("id"))
            logger.info(log)
            print(log)
            self.products_data.append(data)
    
    def create_items(self):
        for product_data in self.products_data:
            product_id = product_data.get("data", {}).get("id")
            url = self.products_url.format(product_id=product_id)
            response = self.session.put(url, json=product_data)
            if response.status_code >= 500:
                logger.info("put product status_code {}".format(response.status_code))
                continue
            json_resp = response.json()
            message = json_resp.get("error", {}).get("message")
            if response.status_code == 201:
                access_token = json_resp.get("access", {}).get("token")
                message = "Create {}".format(access_token)
            log = "{} : {}".format(product_id, message)
            logger.info(log)
            print(log)


if __name__ == "__main__":
    wb = load_workbook(filename=XLSX_FILE_NAME)
    for ws in wb:
        products = Products(ws)
        products.parse_file()
        products.create_items()

