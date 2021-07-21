import requests
from openpyxl import load_workbook
from framework import Parser


wb = load_workbook(filename='Products.xlsx')
ws = wb['example']

parser = Parser(ws)
session = requests.Session()
session.auth = ('12345678', 'selftest')
result = []


def main():
    for row in ws.rows:
        parser.json_data = {"status": "active"}
        parser.json_access = {}
        for cell in row:
            value = cell.value
            if value is None:
                break
            key = parser.get_key(cell)
            if value == "true":
                value = True
            elif value == "false":
                value = False
            method = parser.get_method_by_key(key)
            if method:
                method(key, value)
        data = {
            "access": parser.json_access,
            "data": parser.json_data
        }
        result.append(data)


if __name__ == "__main__":
    main()

    for res in result[1:]:
        product_id = res["data"]["id"]
        url = "https://catalog-test.prozorro.ua/api/0/products/{product_id}".format(product_id=product_id)
        response = session.put(url, json=res)
        print(response.json())
