# MOJIZA/projectpapca/page_qrcode.py

from engine.engine import PAGE, HTML
from PyCSS.PyCSS import PyCSS
import qrcode
import io
import base64

@PAGE(type="page", pagename="qrcode", route="/qrcode", methods=["GET", "POST"])
def qrcode_page(request, response):
    if request.method == "GET":
        # GET so'rovi uchun HTML sahifa yaratish
        styles = PyCSS()
        styles.add_class("QRCodeClass", background_color="white", font_size="16px", padding="20px", text_align="center")
        css = styles.render()

        page = HTML(title_document="QR Code Generator")
        page.add_styles(css)

        qrcode_div = page.div(h_id="qrcodeID", h_class="QRCodeClass")

        qrcode_div.h1("QR Code Generator")
        qrcode_div.p("Enter the text you want to convert to a QR Code:")

        # Form yaratish
        form = qrcode_div.form(action="/qrcode", method="POST")
        form.input(name="text", placeholder="Enter text here", required=True)
        form.button("Generate QR Code", type="submit")

        qrcode_div.p("<a href='/'>Back to Home</a>")

        response.set_body(page.end(
            AUTHOR="Muhiddinov Abdulhodiy{Exaction}"
        ))
        response.send()
    
    elif request.method == "POST":
        # POST so'rovi uchun QR kod yaratish
        text = request.body.get('text', [''])[0]
        if not text:
            response.set_body("<h1>Error: No text provided.</h1><a href='/qrcode'>Try Again</a>")
            response.send()
            return

        # QR kodini yaratish
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(text)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")

        # Image-ni bytes ga aylantirish
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        img_bytes = buffered.getvalue()

        # Image-ni base64 ga aylantirish
        img_base64 = base64.b64encode(img_bytes).decode()

        # HTML sahifa yaratish
        styles = PyCSS()
        styles.add_class("QRCodeResultClass", background_color="white", font_size="16px", padding="20px", text_align="center")
        css = styles.render()

        page = HTML(title_document="QR Code Result")
        page.add_styles(css)

        result_div = page.div(h_id="resultID", h_class="QRCodeResultClass")

        result_div.h1("Your QR Code")
        # QR kodini rasm sifatida ko'rsatish
        result_div.img(src=f"data:image/png;base64,{img_base64}", alt="QR Code")
        result_div.p("Scan the QR code above to access the content.")

        # Qayta QR kod yaratish uchun havola
        result_div.p("<a href='/qrcode'>Generate Another QR Code</a>")

        response.set_body(page.end(
            AUTHOR="Muhiddinov Abdulhodiy{Exaction}"
        ))
        response.send()
