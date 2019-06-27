import json
import requests
import math
import urllib.parse
import typing

class JsonReader:
    def read_json(self, json_obj : str):
        pass 

class JsonWriter:
    @staticmethod
    def write_json(json_obj):
        pass 

class Vector2(JsonReader):
    def __init__(self, x = None, y = None):
        self.x = x
        self.y = y

    @staticmethod
    def from_http(data):
        json_obj = json.loads(data)
        return Vector2(json_obj['x'], json_obj['y'])

class API:
    def post(self, body : Vector2, hello : float) -> str:
        return hello

def serve(schema):
    def handle(request : requests.Request) -> requests.Response:
        url_obj = urllib.parse.urlparse(request.url)
        if request.method in ["POST", "GET", "PUT", "DELETE"]:
            # get into snake case
            method_str = request.method.lower()

            try:
                method = getattr(schema, method_str)
            except AttributeError as e:
                resp = requests.Response()
                resp.status_code = requests.status_codes.codes.not_allowed
                resp.reason = "method {request.method} allowed"
                return resp

            body = method.__annotations__['body'].from_http(request.data)

            # refining query dict
            query_obj = urllib.parse.parse_qs(url_obj.query)
            for v, t in method.__annotations__.items():
                if v == 'body':
                    continue
                if not isinstance(t, typing.Sequence):
                    if v in query_obj:
                        query_obj[v] = query_obj[v][0]
            result = method(schema, body, **query_obj)

            # build response
            resp = requests.Response()
            resp.status_code = requests.status_codes.codes.ok 
            if method.__annotations__['return'] in [str, float, int, None]:
                resp.raw = result 
                resp.encoding = "utf-8"
                resp.headers['content-encoding'] = 'text/plain'
            else:
                resp.raw = json.dumps(result.__dict__)
                resp.encoding = "utf-8"
                resp.headers['content-encoding'] = 'application/json'
            return resp
        else:
            resp = requests.Response()
            resp.status_code = requests.status_codes.codes.not_allowed
            resp.reason = "method {request.method} allowed"
            return resp
    return handle

print(serve(API)(requests.Request("POST", "/hello?hello=7", data = "{\"x\": 3, \"y\": 4}")).raw)