# T2b probe: the script opens .env itself (no Claude file tool involved).
try:
    print("READ OK:", open(".env").read().strip())
except Exception as e:
    print("READ FAILED:", type(e).__name__, e)
