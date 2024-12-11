# MOJIZA/engine/error_handler.py

def handle_404(response):
    response.set_status(404)
    response.set_body("<h1>404 Not Found</h1>")
    response.send()

def handle_500(response, error):
    response.set_status(500)
    response.set_body(f"<h1>500 Internal Server Error</h1><p>{str(error)}</p>")
    response.send()
