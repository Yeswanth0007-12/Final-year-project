import requests
import time
import json
import traceback

BASE_URL = "http://localhost:8000"

print("Starting scan...", flush=True)
resp = requests.post(f"{BASE_URL}/executive-scan")
if resp.status_code != 200:
    print("Failed to start:", resp.text, flush=True)
    exit(1)

scan_id = resp.json()["scan_id"]
print(f"Scan started, ID: {scan_id}", flush=True)

while True:
    try:
        endpoints = ['vulnerabilities', 'dashboard', 'system-core']
        all_good = True
        statuses = {}
        for ep in endpoints:
            r = requests.get(f"{BASE_URL}/{ep}")
            if r.status_code != 200:
                print(f"Error on /{ep}: {r.status_code} - {r.text}", flush=True)
                all_good = False
            else:
                data = r.json()
                if ep == 'vulnerabilities':
                    for v in data:
                        s = v.get("status", "UNKNOWN")
                        statuses[s] = statuses.get(s, 0) + 1

        print(f"[{time.strftime('%H:%M:%S')}] Statuses: {statuses}")
        
        # Add output to manually verify if empty arrays are returned
        dashboard_r = requests.get(f"{BASE_URL}/dashboard")
        print(f"Dashboard data: {dashboard_r.json()}", flush=True)

        if statuses.get("FIXED", 0) > 0 and statuses.get("QUEUED_FOR_PATCH", 0) == 0 and statuses.get("VALIDATING", 0) == 0 and statuses.get("PATCH_APPLIED", 0) == 0 and statuses.get("PATCH_GENERATING", 0) == 0:
            print(f"\n[{time.strftime('%H:%M:%S')}] All patches finished!", flush=True)
            break
            
        time.sleep(2)
    except Exception as e:
        print(f"\nException: {traceback.format_exc()}", flush=True)
        time.sleep(2)

print("\nFinal vulnerabilities data structure:")
print(json.dumps(data[0] if data and isinstance(data, list) else {}, indent=2), flush=True)
