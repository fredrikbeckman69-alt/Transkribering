
import urllib.request
import urllib.parse
import urllib.error

PROXY_URL = "https://corsproxy.io/?"
TARGET_URL = "https://router.huggingface.co/hf-inference/models/KBLab/whisper-large-v3-swedish"
API_URL = PROXY_URL + urllib.parse.quote(TARGET_URL)

def test_url(url, name):
    print(f"Testing {name}: {url}")
    req = urllib.request.Request(url, data=b"fake_audio_data", headers={"Content-Type": "application/octet-stream"})
    try:
        with urllib.request.urlopen(req) as response:
            print(f"{name} Status Code: {response.getcode()}")
            print(f"{name} Response excerpt: {response.read(200)}")
    except urllib.error.HTTPError as e:
        print(f"{name} HTTP Error: {e.code}")
        print(f"{name} Error Response: {e.read(200)}")
    except Exception as e:
        print(f"{name} Request failed: {e}")

if __name__ == "__main__":
    test_url(TARGET_URL, "Direct")
    print("-" * 20)
    test_url(API_URL, "Proxy")
