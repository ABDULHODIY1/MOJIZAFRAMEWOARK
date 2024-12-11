# MOJIZA Framework

MOJIZA - bu oddiy va kengaytiriladigan Python asosidagi web framework bo'lib, tez va oson HTML sahifalar yaratish imkonini beradi. Bu framework sizga HTML elementlarini dinamik tarzda yaratish, CSS uslublarini qo'shish va routing tizimini boshqarish imkonini beradi.
## HOZIRDA USHBU FRAME WOARK BILAN QILINGAN LOIXA BU QRCODE WEB ILOVASI LOIXASI BOLDI U FRAMEWOARK BILAN BITTA FAYLDA JOYLASHGANI SABABLI SIZ U KODNI TEKSHIRISHINGIZ VA OZINGIZ UCHUN QOLLASHINGIZ YOKI OZGARTIRISHINGGIZ MUMKIN TAKLIF VA MUROJATLAR BOLSA MUHIDDINOV ABDULHODIYGA MUROJAT QILISHINGIZ MUMKIN

## XOZIRCHA USHBU FRAMEWORK USTIDA ISHLANMOQDA

## Xususiyatlari

- **Oson HTML Elementlarini Yaratish:** Dinamik HTML teglarini yaratish va ularni o'zaro bog'lash imkoniyati.
- **CSS Uslublarini Boshqarish:** PyCSS yordamida CSS klasslarini yaratish va HTML elementlariga qo'shish.
- **Routing Tizimi:** URL yo'nalishlarini boshqarish va sahifalarni ularga biriktirish.
- **Auto-Reload:** Kod o'zgarishlarini avtomatik tarzda qayta yuklash.
- **Muallif Ma'lumotlari:** JavaScript orqali muallif ma'lumotlarini konsolga chiqarish.

## O'rnatish


1. **Virtual Muhitni Yaratish va Faollashtirish:**

    ```bash
    python -m venv venv
    source venv/bin/activate  # MacOS/Linux
    venv\Scripts\activate     # Windows
    ```

2. **Kerakli Kutubxonalarni O'rnatish:**

    ```bash
    pip install -r requirements.txt
    ```

    **`requirements.txt` tarkibi:**

    ```
    watchdog
    qrcode
    Pillow
    watchdog
    ```

## Foydalanish

1. **Sahifa Fayllarini Yaratish:**

    `projectpapca` katalogida yangi sahifa fayllarini yarating (`page1.py`, `page2.py`, `page_home.py`).

2. **Sahifalar Kodini Yozish:**

    Har bir sahifa faylida `@PAGE` dekoratoridan foydalanib, sahifa funksiyalarini yarating.

    ```python
    # MOJIZA/projectpapca/page_home.py

    from engine.engine import PAGE, HTML
    from PyCSS.PyCSS import PyCSS

    @PAGE(type="page", pagename="home", route="/")
    def home_page():
        styles = PyCSS()
        styles.add_class("HomeClass", color="black", font_size="20px", width="800px", height="600px")
        css = styles.render()

        page = HTML(title_document="Home Page")
        page.add_styles(css)

        home = page.div(h_id="homeID", h_class="HomeClass")
        home.h1(text="Welcome to MOJIZA Framework!")
        home.p(text="This is the home page.")

        response = page.end(
            AUTHOR="Muhiddinov Abdulhodiy{Exaction}"
        )

        return response
    ```

3. **Serverni Ishga Tushurish:**

    ```bash
    python manage.py
    ```

4. **Brauzerda Sahifalarni Ko'rish:**

    - Home Page: [http://localhost:8000/](http://localhost:8000/)
    - Contact Page: [http://localhost:8000/contact](http://localhost:8000/contact)
    - Services Page: [http://localhost:8000/services](http://localhost:8000/services)

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## License

MIT License

## Muallif

**Muhiddinov Abdulhodiy**  
Email: contact@mojiza.com  
GitHub: [@abdulhodiy](https://github.com/abdulhodiy)
# MyFramewoark
# MOJIZAFRAMEWOARK
