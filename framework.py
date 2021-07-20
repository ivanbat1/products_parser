import requests


class Parser:

    json_data = {}
    json_access = {}
    code_by_id = {}

    def __init__(self, ws):
        self.ws = ws
        self.session = requests.Session()

    def get_key(self, cell):
        col = cell.col_idx
        key = self.ws.cell(1, col).value
        return key.strip()

    def get_method_by_key(self, key):
        if key is None or "image" in key:
            return
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

    def requirement_responses(self, key, value):
        self.json_data.setdefault("requirementResponses", [])
        self.json_data["requirementResponses"].append({
            "requirement": key,
            "value": value,
            "id": self.code_by_id.get(key)
        })
        pass

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
        url = "https://catalog-test.prozorro.ua/api/0/profiles/{profile_id}".format(profile_id=value)
        response = self.session.get(url)
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
