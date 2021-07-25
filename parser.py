import requests
from openpyxl import load_workbook
from constants import URL_NAME, XLSX_FILE_NAME, SHEET_NAME, AUTH
from framework import Parser


class Products:
    products_data = []
    
    def __init__(self, ws):
        self.ws = ws
        self.parser = Parser(ws)
        self.session = requests.Session()
        self.session.auth = AUTH

    def parse_file(self):
        for row in self.ws.rows:
            self.parser.json_data = {"status": "active"}
            self.parser.json_access = {}
            for cell in row:
                value = cell.value
                if value is None:
                    break
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
            print('parse {}'.format(data.get("data", {}).get("id")))
            self.products_data.append(data)
    
    def create_items(self):
        for res in self.products_data[1:]:
            product_id = res.get("data", {}).get("id")
            url = URL_NAME + "/api/0/products/{product_id}".format(product_id=product_id)
            response = self.session.put(url, json=res)
            if response.status_code >= 500:
                print("put product status_code {}".format(response.status_code))
                continue
            json_resp = response.json()
            message = json_resp.get("error", {}).get("message")
            if response.status_code == 201:
                access_token = json_resp.get("access", {}).get("token")
                message = "Create {}".format(access_token)
            log = "{} : {}".format(product_id, message)
            print(log)


if __name__ == "__main__":
    wb = load_workbook(filename=XLSX_FILE_NAME)
    #ws = wb[SHEET_NAME]
    for ws in wb:
        products = Products(ws)
        products.parse_file()
        products.create_items()

