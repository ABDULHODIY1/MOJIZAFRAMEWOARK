# MOJIZA/engine/engine.py

import sys
import os
import importlib
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse
import json
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import threading
import time
import sqlite3
from contextlib import contextmanager
import uuid
import qrcode
import io
import base64

# ----------------------------
# Router Module
# ----------------------------
class Router:
    def __init__(self):
        # routes structure: {path: {method: view_func}}
        self.routes = {}
    
    def add_route(self, path, method, view_func):
        if path not in self.routes:
            self.routes[path] = {}
        self.routes[path][method.upper()] = view_func
    
    def get_view(self, path, method):
        method = method.upper()
        if path in self.routes and method in self.routes[path]:
            return self.routes[path][method]
        return None

# ----------------------------
# Request Module
# ----------------------------
class Request:
    def __init__(self, handler):
        self.handler = handler
        self.method = handler.command
        self.path = handler.path
        self.headers = handler.headers
        self.query = {}
        self.body = {}
        self.session = {}
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

# ----------------------------
# Response Module
# ----------------------------
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

# ----------------------------
# Middleware Module
# ----------------------------
class Middleware:
    def __init__(self):
        self.middlewares = []
    
    def add(self, func):
        self.middlewares.append(func)
    
    def execute(self, request, response):
        for middleware in self.middlewares:
            middleware(request, response)

middleware = Middleware()

# ----------------------------
# Sessions Module
# ----------------------------
class SessionManager:
    def __init__(self):
        self.sessions = {}
    
    def create_session(self):
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = {}
        return session_id
    
    def get_session(self, session_id):
        return self.sessions.get(session_id, {})
    
    def set_session_data(self, session_id, key, value):
        if session_id in self.sessions:
            self.sessions[session_id][key] = value
    
    def get_session_data(self, session_id, key):
        return self.sessions.get(session_id, {}).get(key, None)

session_manager = SessionManager()

# ----------------------------
# Sessions Middleware
# ----------------------------
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

# ----------------------------
# Logging Middleware
# ----------------------------
def logging_middleware(request, response):
    print(f"{request.method} request to {request.path}")

middleware.add(logging_middleware)

# ----------------------------
# Database Module
# ----------------------------
DB_NAME = 'mojiza.db'

@contextmanager
def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.commit()
        conn.close()

def init_db():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        # Foydalanuvchilar jadvalini yaratish
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL
            )
        ''')

# ----------------------------
# Error Handling Module
# ----------------------------
def handle_404(response):
    response.set_status(404)
    response.set_body("<h1>404 Not Found</h1><p>The requested resource was not found on this server.</p>")
    response.send()

def handle_500(response, error):
    response.set_status(500)
    response.set_body(f"<h1>500 Internal Server Error</h1><p>{str(error)}</p>")
    response.send()

# ----------------------------
# HTML Rendering Classes
# ----------------------------
class HTMLElement:
    def __init__(self, tag, **attrs):
        self.tag = tag
        self.attrs = {}
        self.children = []
        self.content = ""
        
        for key, value in attrs.items():
            if key.startswith('h_'):  # Handle special attributes
                attr_name = key[2:]
                self.attrs[attr_name] = value
            else:
                self.attrs[key] = value

    def __call__(self, *args, **kwargs):
        for child in args:
            if isinstance(child, HTMLElement) or isinstance(child, str):
                self.children.append(child)
        return self

    def set_content(self, content):
        self.content = content
        return self

    def add_class(self, class_name):
        if 'class' in self.attrs:
            self.attrs['class'] += f" {class_name}"
        else:
            self.attrs['class'] = class_name
        return self

    def add_id(self, id_name):
        self.attrs['id'] = id_name
        return self

    def add_style(self, **styles):
        style_str = self.attrs.get('style', '')
        for prop, value in styles.items():
            style_str += f"{prop.replace('_', '-')}:{value}; "
        self.attrs['style'] = style_str.strip()
        return self

    def __getattr__(self, tag_name):
        def create_element(*args, **attrs):
            element = HTMLElement(tag_name, **attrs)
            self.children.append(element)
            for child in args:
                if isinstance(child, HTMLElement) or isinstance(child, str):
                    element(child)
            return element
        return create_element

    def render(self, indent=0):
        indent_space = '    ' * indent
        attrs_str = ' '.join([f'{key}="{value}"' for key, value in self.attrs.items()])
        
        self_closing_tags = ['meta', 'link', 'img', 'input', 'br', 'hr', 'source', 'embed', 
                             'param', 'area', 'base', 'col', 'command', 'keygen', 'track', 'wbr']
        
        if self.tag in self_closing_tags:
            opening_tag = f"<{self.tag} {attrs_str}/>" if attrs_str else f"<{self.tag}/>"
            return f"{indent_space}{opening_tag}\n"
        else:
            opening_tag = f"<{self.tag} {attrs_str}>" if attrs_str else f"<{self.tag}>"
            closing_tag = f"</{self.tag}>"

            inner_html = ""
            if self.content:
                inner_html += f"{indent_space}    {self.content}\n"
            for child in self.children:
                if isinstance(child, HTMLElement):
                    inner_html += child.render(indent + 1)
                else:
                    inner_html += f"{'    ' * (indent + 1)}{child}\n"

            if self.children or self.content:
                return f"{indent_space}{opening_tag}\n{inner_html}{indent_space}{closing_tag}\n"
            else:
                return f"{indent_space}{opening_tag}{closing_tag}\n"

class HTML:
    def __init__(self, title_document, lang="en", **attrs):
        self.doctype = "<!DOCTYPE html>"
        self.html = HTMLElement('html', h_lang=lang, **attrs)

        self.head = HTMLElement('head')
        self.html.children.append(self.head)

        meta_charset = HTMLElement('meta', h_charset="UTF-8")
        self.head.children.append(meta_charset)

        meta_viewport = HTMLElement('meta', h_name="viewport", h_content="width=device-width, initial-scale=1.0")
        self.head.children.append(meta_viewport)

        title = HTMLElement('title').set_content(title_document)
        self.head.children.append(title)

        self.body = HTMLElement('body')
        self.html.children.append(self.body)

    def __getattr__(self, tag_name):
        def create_element(*args, **attrs):
            element = HTMLElement(tag_name, **attrs)
            self.body.children.append(element)
            for child in args:
                if isinstance(child, HTMLElement) or isinstance(child, str):
                    element(child)
            return element
        return create_element

    # Standart HTML elementlari uchun metodlar
    def a(self, href="", text="", **attrs):
        a = HTMLElement('a', href=href, **attrs).set_content(text)
        self.body.children.append(a)
        return a

    # Qo'shimcha HTML teglarini yaratish uchun metodlar
    def div(self, **attrs):
        div = HTMLElement('div', **attrs)
        self.body.children.append(div)
        return div

    def span(self, **attrs):
        span = HTMLElement('span', **attrs)
        self.body.children.append(span)
        return span

    def ul(self, **attrs):
        ul = HTMLElement('ul', **attrs)
        self.body.children.append(ul)
        return ul

    def li(self, **attrs):
        li = HTMLElement('li', **attrs)
        self.body.children.append(li)
        return li

    def form(self, **attrs):
        form = HTMLElement('form', **attrs)
        self.body.children.append(form)
        return form

    def button(self, text="", **attrs):
        button = HTMLElement('button', **attrs).set_content(text)
        self.body.children.append(button)
        return button

    def table(self, **attrs):
        table = HTMLElement('table', **attrs)
        self.body.children.append(table)
        return table

    def tr(self, **attrs):
        tr = HTMLElement('tr', **attrs)
        self.body.children.append(tr)
        return tr

    def td(self, text="", **attrs):
        td = HTMLElement('td', **attrs).set_content(text)
        self.body.children.append(td)
        return td

    def add_styles(self, css):
        """
        CSS kodini head bo'limiga qo'shish.
        :param css: CSS kodi satri yoki URL manzili
        """
        if css.startswith('/static/'):
            # Static CSS faylini ulash
            self.link_tag(href=css, rel='stylesheet')
        else:
            # Inline CSS
            style = HTMLElement('style').set_content(css)
            self.head.children.append(style)
        return self

    def add_script(self, script_content):
        """
        JavaScript kodini body bo'limiga qo'shish.
        :param script_content: JavaScript kodi satri yoki URL manzili
        """
        if script_content.startswith('/static/'):
            # Static JS faylini ulash
            self.script_tag(src=script_content)
        else:
            # Inline JS
            script = HTMLElement('script').set_content(script_content)
            self.body.children.append(script)
        return self

    def end(self, sleep=0, LOGGER=False, DEBUGS=True, AUTHOR="", others=0):
        """
        HTML hujjatini yakunlash va render qilish.
        Qo'shimcha parametrlar orqali loglash yoki debugging qilish mumkin.
        :param sleep: Uyqusizlik (hozircha ishlatilmaydi)
        :param LOGGER: Loglash (hozircha ishlatilmaydi)
        :param DEBUGS: Debug rejimi
        :param AUTHOR: Muallif ma'lumotlari
        :param others: Qo'shimcha parametrlar
        :return: Render qilingan HTML kodi
        """
        if AUTHOR:
            script_content = f'''
const INFORMATION = `
THIS SITE CREATED BY {AUTHOR}!
:_________FRAMEWORK__INFO_________:
: VERSION: 1.0.0                  :
: FRAMEWORK NAME: MOJIZA          :
: AUTHOR: {AUTHOR}                :
: USING WITH PYTHON               :
:_________FRAMEWORK__INFO_________:
`;
            '''
            self.add_script(script_content)
        
        return self.doctype + "\n" + self.html.render()

# ----------------------------
# PAGE Decorator
# ----------------------------
router = Router()

def PAGE(type, pagename, route, methods=["GET"]):
    """
    PAGE dekoratori sahifa funksiyasini routing tizimiga qo'shish uchun ishlatiladi.
    :param type: 'page' bo‘lishi kerak
    :param pagename: Sahifaning nomi (masalan, 'home')
    :param route: URL yo‘nalishi (masalan, '/', '/login')
    :param methods: HTTP metodlari ro'yxati (default: ["GET"])
    """
    if type != "page":
        raise ValueError("PAGE dekoratorining 'type' parametri faqat 'page' bo'lishi mumkin.")
    
    def decorator(view_func):
        for method in methods:
            router.add_route(route, method, view_func)
        return view_func
    return decorator

# ----------------------------
# Error Handler Module
# ----------------------------
def handle_404(response):
    response.set_status(404)
    response.set_body("<h1>404 Not Found</h1><p>The requested resource was not found on this server.</p>")
    response.send()

def handle_500(response, error):
    response.set_status(500)
    response.set_body(f"<h1>500 Internal Server Error</h1><p>{str(error)}</p>")
    response.send()

# ----------------------------
# Sessions Module
# ----------------------------
# (Already defined above)

# ----------------------------
# Initialize Database
# ----------------------------
def initialize():
    init_db()

# ----------------------------
# Request Handler Class
# ----------------------------
class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.handle_request()

    def do_POST(self):
        self.handle_request()
    
    def do_PUT(self):
        self.handle_request()
    
    def do_DELETE(self):
        self.handle_request()
    
    def handle_request(self):
        request = Request(self)
        response = Response(self)
        
        # Execute middleware functions
        middleware.execute(request, response)
        
        if request.path.startswith("/static/"):
            self.handle_static(request.path)
            return
        
        view = router.get_view(request.path, request.method)
        if view:
            try:
                view(request, response)
            except Exception as e:
                handle_500(response, e)
        else:
            handle_404(response)
    
    def handle_static(self, path):
        static_dir = os.path.join(os.path.dirname(__file__), '..', 'static')
        file_path = os.path.join(static_dir, path.lstrip('/static/'))
        if os.path.isfile(file_path):
            self.send_response(200)
            if file_path.endswith('.css'):
                self.send_header('Content-Type', 'text/css')
            elif file_path.endswith('.js'):
                self.send_header('Content-Type', 'application/javascript')
            elif file_path.endswith('.png'):
                self.send_header('Content-Type', 'image/png')
            elif file_path.endswith('.jpg') or file_path.endswith('.jpeg'):
                self.send_header('Content-Type', 'image/jpeg')
            else:
                self.send_header('Content-Type', 'application/octet-stream')
            self.end_headers()
            with open(file_path, 'rb') as f:
                self.wfile.write(f.read())
        else:
            handle_404(Response(self))

# ----------------------------
# Watchdog Event Handler
# ----------------------------
class ReloadHandler(FileSystemEventHandler):
    def __init__(self, callback):
        super(ReloadHandler, self).__init__()
        self.callback = callback

    def on_modified(self, event):
        if not event.is_directory and event.src_path.endswith('.py'):
            print(f"Detected change in {event.src_path}. Reloading...")
            self.callback()

# ----------------------------
# Auto-reload Function
# ----------------------------
def start_auto_reload(callback):
    projectpapca_path = os.path.join(os.path.dirname(__file__), '..', 'projectpapca')
    event_handler = ReloadHandler(callback)
    observer = Observer()
    observer.schedule(event_handler, path=projectpapca_path, recursive=True)
    observer.start()
    print("Auto-reload started. Watching for changes in projectpapca...")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

# ----------------------------
# Server Runner Function
# ----------------------------
def run_server(port=8000):
    server_address = ('', port)
    httpd = HTTPServer(server_address, RequestHandler)
    print(f"Starting server on port {port}...")
    httpd.serve_forever()

# ----------------------------
# Reload Server Function
# ----------------------------
def reload_server():
    print("Reloading server...")
    projectpapca_path = os.path.join(os.path.dirname(__file__), '..', 'projectpapca')
    for filename in os.listdir(projectpapca_path):
        if filename.endswith('.py') and filename != '__init__.py':
            module_name = f"projectpapca.{os.path.splitext(filename)[0]}"
            if module_name in sys.modules:
                try:
                    importlib.reload(sys.modules[module_name])
                    print(f"Reloaded module: {module_name}")
                except Exception as e:
                    print(f"Failed to reload module {module_name}: {e}")
            else:
                try:
                    importlib.import_module(module_name)
                    print(f"Imported new module: {module_name}")
                except Exception as e:
                    print(f"Failed to import module {module_name}: {e}")
    print("Server reloaded.")

# ----------------------------
# Main Function
# ----------------------------
def main():
    # Add project directory to PYTHONPATH
    project_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, project_dir)

    # Initialize the database
    initialize()

    # Import all pages in projectpapca
    pages = [f for f in os.listdir(os.path.join(project_dir, 'projectpapca')) if f.endswith('.py')]
    for page in pages:
        module_name = os.path.splitext(page)[0]
        if module_name != '__init__':
            try:
                importlib.import_module(f'projectpapca.{module_name}')
                print(f"Imported module: projectpapca.{module_name}")
            except Exception as e:
                print(f"Failed to import module projectpapca.{module_name}: {e}")

    # Start server in a separate thread
    server_thread = threading.Thread(target=run_server, args=(8000,), daemon=True)
    server_thread.start()

    # Start auto-reload in a separate thread
    reload_thread = threading.Thread(target=start_auto_reload, args=(reload_server,), daemon=True)
    reload_thread.start()

    # Keep the main thread alive
    server_thread.join()
    reload_thread.join()

# ----------------------------
# Run the main function
# ----------------------------
if __name__ == "__main__":
    main()

# ----------------------------
# HTML Rendering and Router Usage
# ----------------------------
# Note: The HTML and HTMLElement classes are defined above. Use them in your page modules as needed.

# Example Page Module Usage:
# In your `projectpapca/page_example.py`, use the @PAGE decorator to register routes.
