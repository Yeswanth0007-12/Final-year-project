import requests
import time

BASE_URL = "http://localhost:8000"
print("Scanning backend payload...")

while True:
    try:
        r_dash = requests.get(f"{BASE_URL}/dashboard").json()
        r_vuln = requests.get(f"{BASE_URL}/vulnerabilities").json()
        r_pipe = requests.get(f"{BASE_URL}/pipeline/status").json()
        
        print(f"[{time.strftime('%H:%M:%S')}] Vulns: {len(r_vuln) if isinstance(r_vuln, list) else 'ERR_NOT_LIST'}, Dash: {r_dash.get('patched', 'ERR')}, Queue: {len(r_pipe.get('queue', []))}")
        time.sleep(2)
    except Exception as e:
        print(f"Crash: {e}")
        time.sleep(2)
