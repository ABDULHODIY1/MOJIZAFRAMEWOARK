# MOJIZA/engine/routors.py

class Route:
    def __init__(self, route, view):
        """
        Route obyektini yaratish.
        :param route: URL yo‘nalishi (masalan, '/', '/hello')
        :param view: View funksiyasi
        """
        self.route = route
        self.view = view


# MOJIZA/engine/routors.py

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
