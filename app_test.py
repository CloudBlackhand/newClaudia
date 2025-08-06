#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
App de Teste Ultra-Básico
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
from datetime import datetime

class TestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {"status": "healthy", "timestamp": str(datetime.now())}
            self.wfile.write(json.dumps(response).encode())
        elif self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            html = f"""
            <!DOCTYPE html>
            <html>
            <head><title>Teste Railway</title></head>
            <body>
                <h1>✅ Sistema Online</h1>
                <p>Timestamp: {datetime.now()}</p>
                <p>Path: {self.path}</p>
            </body>
            </html>
            """
            self.wfile.write(html.encode())
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not Found")

if __name__ == "__main__":
    server = HTTPServer(('0.0.0.0', 8000), TestHandler)
    print("🚀 Servidor iniciado na porta 8000")
    print("🌐 Healthcheck: http://0.0.0.0:8000/health")
    print("📄 Página: http://0.0.0.0:8000/")
    server.serve_forever() 