# MOJIZA/projectpapca/page_faq.py

from engine.engine import PAGE, HTML
from PyCSS.PyCSS import PyCSS

@PAGE(type="page", pagename="faq", route="/faq")
def faq_page():
    styles = PyCSS()
    styles.add_class("FaqClass", background_color="lightgray", font_size="16px", padding="20px")
    css = styles.render()

    page = HTML(title_document="FAQ")
    page.add_styles(css)

    faq_div = page.div(h_id="faqID", h_class="FaqClass")

    faq_div.h1("Frequently Asked Questions")
    faq_div.p("Here are some common questions and answers.")

    # Misol uchun, savollar va javoblar
    faq_div.h2("Q1: How does MOJIZA work?")
    faq_div.p("A1: MOJIZA is a Python-based framework that allows you to create dynamic HTML pages easily.")

    faq_div.h2("Q2: How can I add a new page?")
    faq_div.p("A2: Follow the steps outlined in the documentation to add a new page.",style="color:red;")

    response = page.end(
        AUTHOR="Muhiddinov Abdulhodiy{Exaction}"
    )

    return response
