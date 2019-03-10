import json
import requests
import pprint
from datetime import datetime


class Request:

    def __init__(self, token, store_name):
        self.token = token
        self.store_name = store_name

        self.request = requests.Session()
        self.protocol = 'https'
        self.version_api = 'v1'

        self.init_request()

    def init_request(self):
        authorization = {'Authorization': 'Bearer {}'.format(self.token)}
        content_type = {'Content-Type': 'application/json'}

        self.request.headers.update(authorization)
        self.request.headers.update(content_type)

    def get_list(self, list):
        url_request = '{}://{}/api/{}/{}'.format(self.protocol, self.store_name, self.version_api, list)
        request = self.request.get(url_request)
        json_request = json.loads(request.text)

        list_response = []
        for json_file in json_request:
            list_response.append(Response(json_file))

        return list_response


class Response:

    def __init__(self, json_file):
        self.json_file = json_file

    def print_json(self):
        pprint.pprint(self.json_file)

    def by_key(self, key):
        return self.json_file[key]

    def by_key_float(self, key):
        result = 0
        if is_valid(self.by_key(key)):
            result = float(self.by_key(key))

        return result

    def by_key_int(self, key):
        result = int(self.by_key_float(key))
        return result

    def by_key_date(self, key):
        return parse_date(self.by_key(key))

    def by_key_bool(self, key):
        return self.by_key(key) == 'true'

    def by_key_dict(self, key, value):
        return self.by_key(key)[value]

    def by_key_list(self, key):
        list = []

        for json_file in self.by_key(key):
            list.append(json_file)

        return list

    def by_key_response(self, key):
        list_response_key = []

        for json_file in self.by_key(key):
            list_response_key.append(Response(json_file))

        return list_response_key


def parse_date(date):
    result = None
    try:
        if date != '':
            result = datetime.strptime(date, '%Y-%m-%d')
    except Exception as fail:
        result = None

    return result


def is_valid(number):
    result = False
    if number is not None:
        if number != '':
            result = True

    return result
