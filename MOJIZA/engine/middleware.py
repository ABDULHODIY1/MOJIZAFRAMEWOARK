# MOJIZA/engine/middleware.py

from .sessions import session_manager

class Middleware:
    def __init__(self):
        self.middlewares = []
    
    def add(self, func):
        self.middlewares.append(func)
    
    def execute(self, request, response):
        for middleware in self.middlewares:
            middleware(request, response)

middleware = Middleware()

# Misol uchun, logging middleware qo'shish
def logging_middleware(request, response):
    print(f"{request.method} request to {request.path}")

middleware.add(logging_middleware)

# Sessiya middleware
from .sessions import session_manager

def session_middleware(request, response):
    cookies = request.headers.get('Cookie', '')
    session_id = None
    for cookie in cookies.split(';'):
        if 'session_id=' in cookie:
            session_id = cookie.strip().split('=')[1]
            break
    if not session_id or session_id not in session_manager.sessions:
        session_id = session_manager.create_session()
        response.set_header('Set-Cookie', f'session_id={session_id}; Path=/; HttpOnly')
    request.session = session_manager.get_session(session_id)

middleware.add(session_middleware)
