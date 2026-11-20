import json
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass


@dataclass
class Response:
    status_code: int
    content: bytes

    def json(self):
        return json.loads(self.content)


def http_request(method, url, headers=None, params=None, json_body=None):
    if params:
        url = f"{url}?{urllib.parse.urlencode(params)}"
    request_headers = dict(headers or {})
    body = None
    if json_body is not None:
        body = json.dumps(json_body).encode("utf-8")
        request_headers["Content-Type"] = "application/json"
    request = urllib.request.Request(
        url, data=body, headers=request_headers, method=method
    )
    try:
        with urllib.request.urlopen(request) as response:
            return Response(response.status, response.read())
    except urllib.error.HTTPError as error:
        return Response(error.code, error.read())
