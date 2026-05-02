#!/usr/bin/env python3
"""Static file server with correct MIME types for ES modules."""
import http.server
import socketserver
import sys
import os

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 3457
os.chdir(os.path.dirname(os.path.abspath(__file__)))

class Handler(http.server.SimpleHTTPRequestHandler):
    extensions_map = {
        **http.server.SimpleHTTPRequestHandler.extensions_map,
        '.js':   'application/javascript',
        '.mjs':  'application/javascript',
        '.css':  'text/css',
        '.html': 'text/html',
        '.json': 'application/json',
        '.svg':  'image/svg+xml',
        '':      'application/octet-stream',
    }

    def end_headers(self):
        # Prevent browser caching of HTML, JS, and CSS so edits are always picked up
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        super().end_headers()

    def send_error(self, code, message=None, explain=None):
        # Mirror GitHub Pages behaviour: for missing HTML routes (no extension
        # in the last path segment), serve 404.html so the SPA can hydrate.
        # Real asset 404s (e.g. /css/foo.css that doesn't exist) still return
        # plain 404 so devs notice.
        if code == 404 and '.' not in self.path.rsplit('/', 1)[-1]:
            try:
                with open('404.html', 'rb') as f:
                    body = f.read()
                self.send_response(404)
                self.send_header('Content-Type', 'text/html; charset=utf-8')
                self.send_header('Content-Length', str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                return
            except FileNotFoundError:
                pass
        super().send_error(code, message, explain)

    def log_message(self, format, *args):
        pass  # silence request logging

socketserver.TCPServer.allow_reuse_address = True
with socketserver.ThreadingTCPServer(('', PORT), Handler) as httpd:
    print(f'Serving on port {PORT}')
    httpd.serve_forever()
