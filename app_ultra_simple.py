#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
App Ultra-Simples para Railway - Sem Uvicorn
"""

import os
import json
import time
from http.server import HTTPServer, BaseHTTPRequestHandler

class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        if self.path == '/health':
            response = {"status": "healthy"}
        elif self.path == '/':
            response = {"message": "Claudia Cobranças Online", "status": "ok"}
        else:
            response = {"error": "Not found"}
            
        self.wfile.write(json.dumps(response).encode())
    
    def log_message(self, format, *args):
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {format % args}")

def run_server():
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    print(f"🚀 Iniciando servidor HTTP simples...")
    print(f"📊 PORT: {port}")
    print(f"🌐 HOST: {host}")
    
    server = HTTPServer((host, port), SimpleHandler)
    print(f"✅ Servidor iniciado em http://{host}:{port}")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Servidor parado")
        server.server_close()

if __name__ == "__main__":
    run_server() 