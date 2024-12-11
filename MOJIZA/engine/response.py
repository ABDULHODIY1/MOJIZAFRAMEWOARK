# MOJIZA/engine/response.py

class Response:
    def __init__(self, handler):
        self.handler = handler
        self.status_code = 200
        self.headers = {'Content-Type': 'text/html'}
        self.body = ''
    
    def set_header(self, key, value):
        self.headers[key] = value
    
    def set_status(self, code):
        self.status_code = code
    
    def set_body(self, content):
        self.body = content
    
    def send(self):
        self.handler.send_response(self.status_code)
        for key, value in self.headers.items():
            self.handler.send_header(key, value)
        self.handler.end_headers()
        if isinstance(self.body, str):
            self.body = self.body.encode('utf-8')
        self.handler.wfile.write(self.body)
