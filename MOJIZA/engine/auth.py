# MOJIZA/engine/auth.py

def login_required(view_func):
    def wrapper(request, response):
        username = request.session.get('username')
        if username:
            view_func(request, response)
        else:
            response.set_body("<h1>Access Denied. Please <a href='/login'>login</a>.</h1>")
            response.send()
    return wrapper
