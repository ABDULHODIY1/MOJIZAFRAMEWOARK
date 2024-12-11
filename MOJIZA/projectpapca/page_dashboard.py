# MOJIZA/projectpapca/page_dashboard.py

from engine.engine import PAGE, HTML
from PyCSS.PyCSS import PyCSS
from engine.auth import login_required

@PAGE(type="page", pagename="dashboard", route="/dashboard", methods=["GET"])
@login_required
def dashboard_page(request, response):
    username = request.session.get('username')
    styles = PyCSS()
    styles.add_class("DashboardClass", background_color="lightcoral", font_size="18px", padding="20px", text_align="center")
    css = styles.render()

    page = HTML(title_document="Dashboard")
    page.add_styles(css)

    dashboard_div = page.div(h_id="dashboardID", h_class="DashboardClass")
    dashboard_div.h1(f"Welcome to your dashboard, {username}!")
    dashboard_div.p("Here you can manage your account and settings.")
    dashboard_div.p("<a href='/'>Back to Home</a>")

    response.set_body(page.end(
        AUTHOR="Muhiddinov Abdulhodiy{Exaction}"
    ))
    response.send()
