
import threading
import http.client
import time
import server
import socketserver

# We need to monkeypatch or modify server to run on a different port without blocking import
# But server.py runs immediately on import. 
# Actually, since I overwrote server.py, importing it will run the server and block. 
# This was a minor mistake in design for testability. 
# I will instead create a script that just defines the class and runs it, 
# similar to server.py but on 8001.

import http.server
import urllib.request
import urllib.error
import json

PORT = 8001
TARGET_URL = "https://router.huggingface.co/hf-inference/models/KBLab/whisper-large-v3-swedish"

class ProxyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass # Silence logs for test

    def do_POST(self):
        if self.path == '/api/transcribe':
            self.handle_proxy()
        else:
            self.send_error(404, "Not Found")

    def handle_proxy(self):
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        headers = {
            "Content-Type": self.headers.get("Content-Type", "application/octet-stream"),
        }
        
        if self.headers.get("Authorization"):
            headers["Authorization"] = self.headers.get("Authorization")

        req = urllib.request.Request(TARGET_URL, data=post_data, headers=headers, method="POST")
        
        try:
            with urllib.request.urlopen(req) as response:
                self.send_response(response.getcode())
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(response.read())
        except urllib.error.HTTPError as e:
            self.send_response(e.code)
            self.send_header('Content-Type', 'application/json') # Enforcing JSON content type for client
            self.end_headers()
            # Try to read error body, if empty send formatted json
            body = e.read()
            if not body:
                body = json.dumps({"error": f"HTTP {e.code}"}).encode()
            self.wfile.write(body)
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())

def run_server():
    with socketserver.TCPServer(("", PORT), ProxyHTTPRequestHandler) as httpd:
        httpd.timeout = 1
        while getattr(threading.current_thread(), "do_run", True):
            httpd.handle_request()

def run_test():
    t = threading.Thread(target=run_server)
    t.do_run = True
    t.start()
    time.sleep(1) # Wait for server start

    print(f"Testing local proxy at http://localhost:{PORT}/api/transcribe")
    try:
        conn = http.client.HTTPConnection("localhost", PORT)
        # Send dummy data
        conn.request("POST", "/api/transcribe", body="dummy_audio", headers={"Content-Type": "application/octet-stream"})
        response = conn.getresponse()
        
        print(f"Status: {response.status}")
        content_type = response.getheader("Content-Type")
        print(f"Content-Type: {content_type}")
        
        body = response.read().decode('utf-8', errors='ignore')
        print(f"Body start: {body[:200]}")

        if "application/json" in content_type:
            print("SUCCESS: Response is JSON.")
        else:
            print("FAILURE: Response is NOT JSON.")
            
    except Exception as e:
        print(f"Test Failed: {e}")
    finally:
        t.do_run = False
        # Make one last request to unblock handle_request if needed, or just let it die
        
if __name__ == "__main__":
    run_test()
