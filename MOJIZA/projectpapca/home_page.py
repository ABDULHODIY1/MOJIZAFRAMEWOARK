# MOJIZA/projectpapca/page_home.py

from engine.engine import PAGE, HTML
from PyCSS.PyCSS import PyCSS

@PAGE(type="page", pagename="home", route="/", methods=["GET"])
def home_page(request, response):
    styles = PyCSS()
    styles.add_class("HomeClass", background_color="lightblue", font_size="18px", padding="20px", text_align="center")
    css = styles.render()

    page = HTML(title_document="Home Page")
    page.add_styles(css)

    home_div = page.div(h_id="homeID", h_class="HomeClass")

    home_div.h1("Welcome to MOJIZA Framework!")
    home_div.p("This is the home page. Navigate to other pages using the links below.")

    nav = home_div.nav_tag()
    nav.a("Register", href="/register")
    nav.a("Login", href="/login")
    nav.a("Dashboard", href="/dashboard")
    nav.a("QR Code Generator", href="/qrcode")

    response.set_body(page.end(
        AUTHOR="Muhiddinov Abdulhodiy{Exaction}"
    ))
    response.send()
