# MOJIZA/PyCSS/PyCSS.py

class PyCSS:
    def __init__(self):
        """
        PyCSS sinfini yaratish konstruktori.
        """
        self.styles = {}

    def add_class(self, class_name, **styles):
        """
        CSS klassini qo'shish.
        :param class_name: Klass nomi
        :param styles: CSS xususiyatlari (masalan, color='red')
        """
        self.styles[class_name] = styles
        return self

    def render(self):
        """
        CSS kodini yaratish.
        :return: CSS kodi satri
        """
        css = ""
        for class_name, styles in self.styles.items():
            css += f".{class_name} " + "{\n"
            for prop, value in styles.items():
                css += f"  {prop.replace('_', '-')} : {value};\n"
            css += "}\n"
        return css
