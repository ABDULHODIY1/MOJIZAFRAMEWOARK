# MOJIZA/projectpapca/page_register.py

from engine.engine import PAGE, HTML
from PyCSS.PyCSS import PyCSS
from engine.engine import get_db_connection
import hashlib
import sqlite3

@PAGE(type="page", pagename="register", route="/register", methods=["GET", "POST"])
def register_page(request, response):
    if request.method == "GET":
        # GET so'rovi uchun HTML sahifa yaratish
        styles = PyCSS()
        styles.add_class("RegisterClass", background_color="lightyellow", font_size="16px", padding="20px", text_align="center")
        css = styles.render()

        page = HTML(title_document="Register")
        page.add_styles(css)

        register_div = page.div(h_id="registerID", h_class="RegisterClass")

        register_div.h1("Register")
        form = register_div.form(action="/register", method="POST")
        form.label("Username: ", for_id="username")
        form.input(name="username", placeholder="Enter username", required=True)
        form.label("Password: ", for_id="password")
        form.input(name="password", type="password", placeholder="Enter password", required=True)
        form.button("Register", type="submit")

        register_div.p("<a href='/'>Back to Home</a>")

        response.set_body(page.end(
            AUTHOR="Muhiddinov Abdulhodiy{Exaction}"
        ))
        response.send()
    
    elif request.method == "POST":
        # POST so'rovi uchun ma'lumotlarni qayta ishlash
        username = request.body.get('username', [''])[0]
        password = request.body.get('password', [''])[0]
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        if not username or not password:
            response.set_body("<h1>Error: Username and password are required.</h1><a href='/register'>Try Again</a>")
            response.send()
            return

        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_password))
            response.set_body("<h1>Registration successful!</h1><a href='/login'>Login Here</a>")
        except sqlite3.IntegrityError:
            response.set_body("<h1>Username already exists.</h1><a href='/register'>Try Again</a>")
        response.send()
