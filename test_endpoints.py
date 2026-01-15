
import urllib.request
import urllib.parse
import urllib.error

# Test both endpoints
endpoints = [
    "https://api-inference.huggingface.co/models/KBLab/whisper-large-v3-swedish",
    "https://router.huggingface.co/hf-inference/models/KBLab/whisper-large-v3-swedish"
]

PROXY_URL = "https://corsproxy.io/?"

for endpoint in endpoints:
    print(f"\n{'='*60}")
    print(f"Testing: {endpoint}")
    print(f"{'='*60}")
    
    # Test direct
    print("\n1. Direct (no proxy):")
    req = urllib.request.Request(endpoint, data=b"test", headers={"Content-Type": "application/octet-stream"})
    try:
        with urllib.request.urlopen(req, timeout=5) as response:
            print(f"   Status: {response.getcode()}")
    except urllib.error.HTTPError as e:
        print(f"   HTTP Error: {e.code}")
        body = e.read()[:200]
        print(f"   Response type: {'HTML' if b'<!DOCTYPE' in body or b'<html' in body else 'JSON'}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test with proxy
    print("\n2. Via corsproxy.io:")
    proxy_url = PROXY_URL + urllib.parse.quote(endpoint)
    req = urllib.request.Request(proxy_url, data=b"test", headers={"Content-Type": "application/octet-stream"})
    try:
        with urllib.request.urlopen(req, timeout=5) as response:
            print(f"   Status: {response.getcode()}")
    except urllib.error.HTTPError as e:
        print(f"   HTTP Error: {e.code}")
        body = e.read()[:200]
        print(f"   Response type: {'HTML' if b'<!DOCTYPE' in body or b'<html' in body else 'JSON'}")
    except Exception as e:
        print(f"   Error: {e}")
