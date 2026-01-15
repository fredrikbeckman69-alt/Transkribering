
import http.server
import socketserver
import urllib.request
import urllib.parse
import json
import os
import sys

PORT = 8000
TARGET_URL = "https://router.huggingface.co/hf-inference/models/KBLab/whisper-large-v3-swedish"

class ProxyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/api/transcribe':
            self.handle_proxy()
        else:
            self.send_error(404, "Not Found")

    def handle_proxy(self):
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        # Forward headers
        headers = {
            "Content-Type": self.headers.get("Content-Type", "application/octet-stream"),
        }
        
        auth_header = self.headers.get("Authorization")
        if auth_header:
            headers["Authorization"] = auth_header

        print(f"Proxying request to {TARGET_URL}")
        
        req = urllib.request.Request(TARGET_URL, data=post_data, headers=headers, method="POST")
        
        try:
            with urllib.request.urlopen(req) as response:
                self.send_response(response.getcode())
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(response.read())
        except urllib.error.HTTPError as e:
            self.send_response(e.code)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(e.read())
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            error_response = {"error": str(e)}
            self.wfile.write(json.dumps(error_response).encode())

print(f"Starting server at http://localhost:{PORT}")
print(f"Proxy endpoint: http://localhost:{PORT}/api/transcribe")

# Ensure we are in the script's directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

with socketserver.TCPServer(("", PORT), ProxyHTTPRequestHandler) as httpd:
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
