# MOJIZA/projectpapca/page_login.py

from engine.engine import PAGE, HTML
from PyCSS.PyCSS import PyCSS
from engine.engine import get_db_connection
import hashlib

@PAGE(type="page", pagename="login", route="/login", methods=["GET", "POST"])
def login_page(request, response):
    if request.method == "GET":
        # GET so'rovi uchun HTML sahifa yaratish
        styles = PyCSS()
        styles.add_class("LoginClass", background_color="lightgreen", font_size="16px", padding="20px", text_align="center")
        css = styles.render()

        page = HTML(title_document="Login")
        page.add_styles(css)

        login_div = page.div(h_id="loginID", h_class="LoginClass")

        login_div.h1("Login")
        form = login_div.form(action="/login", method="POST")
        form.label("Username: ", for_id="username")
        form.input(name="username", placeholder="Enter username", required=True)
        form.label("Password: ", for_id="password")
        form.input(name="password", type="password", placeholder="Enter password", required=True)
        form.button("Login", type="submit")

        login_div.p("<a href='/'>Back to Home</a>")

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
            response.set_body("<h1>Error: Username and password are required.</h1><a href='/login'>Try Again</a>")
            response.send()
            return

        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE username=? AND password=?', (username, hashed_password))
            user = cursor.fetchone()
        
        if user:
            # Sessiyani yangilash
            session_id = None
            for cookie in request.headers.get('Cookie', '').split(';'):
                if 'session_id=' in cookie:
                    session_id = cookie.strip().split('=')[1]
                    break
            if session_id:
                request.session['username'] = username
            response.set_body(f"<h1>Welcome, {username}!</h1><a href='/dashboard'>Go to Dashboard</a>")
        else:
            response.set_body("<h1>Invalid credentials.</h1><a href='/login'>Try Again</a>")
        response.send()
