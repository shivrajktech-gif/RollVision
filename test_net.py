import urllib.request

print("Testing internet...")
try:
    with urllib.request.urlopen('http://google.com', timeout=5) as response:
        print(f"✅ Success: {response.status}")
except Exception as e:
    print(f"❌ Failed: {e}")
