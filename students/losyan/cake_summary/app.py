from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer


server = ThreadingHTTPServer(
    ("0.0.0.0", 8000),
    SimpleHTTPRequestHandler
)

print("Open http://localhost:8000", flush=True)
server.serve_forever()