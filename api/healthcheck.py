import urllib.request
import sys

try:
    urllib.request.urlopen("http://localhost:8000/health")
    sys.exit(0)
except Exception:
    sys.exit(1)
