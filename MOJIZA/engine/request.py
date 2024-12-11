# MOJIZA/engine/request.py

from urllib.parse import parse_qs, urlparse
import json

class Request:
    def __init__(self, handler):
        self.handler = handler
        self.method = handler.command
        self.path = handler.path
        self.headers = handler.headers
        self.query = {}
        self.body = {}
        self.parse_url()
        self.parse_body()
    
    def parse_url(self):
        parsed_url = urlparse(self.path)
        self.path = parsed_url.path
        self.query = parse_qs(parsed_url.query)
    
    def parse_body(self):
        if self.method in ['POST', 'PUT', 'PATCH']:
            content_length = int(self.headers.get('Content-Length', 0))
            content_type = self.headers.get('Content-Type', '')
            body = self.handler.rfile.read(content_length).decode('utf-8')
            if 'application/x-www-form-urlencoded' in content_type:
                self.body = parse_qs(body)
            elif 'application/json' in content_type:
                try:
                    self.body = json.loads(body)
                except json.JSONDecodeError:
                    self.body = {}
            else:
                self.body = {}
