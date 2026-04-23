import requests

# This is the Tor proxy running on your machine
proxies = {
    'http': 'socks5h://127.0.0.1:9050',
    'https': 'socks5h://127.0.0.1:9050'
}

# The onion site URL from your assignment
url = "http://tds26vu3ptapxx6igo6n26kuwfpn2l5omkmagc4hc7g7yn2o3xb25syd.onion"

try:
    response = requests.get(url, proxies=proxies, timeout=60)
    print("Status code:", response.status_code)
    print("First 500 characters of HTML:")
    print(response.text[:500])
except Exception as e:
    print("Something went wrong:", e)