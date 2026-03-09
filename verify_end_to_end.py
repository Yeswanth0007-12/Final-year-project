import requests
import time
import json
import sys

API_URL = "http://127.0.0.1:8000"

print("Starting end-to-end automation verification...")

try:
    # 1. Start Executive Scan
    print("\\n[1] Initiating Executive Scan...")
    res = requests.post(f"{API_URL}/executive-scan")
    if res.status_code != 200:
        print(f"Failed to start scan: {res.text}")
        sys.exit(1)
    
    scan_id = res.json().get("scan_id")
    print(f"Scan started with ID: {scan_id}")

    # 2. Poll Terminal Stream until COMPLETED
    print("\\n[2] Polling Scanner Engine...")
    last_idx = 0
    poll_count = 0
    found_count = 0
    while poll_count < 30: # 30 seconds max
        res = requests.get(f"{API_URL}/terminal-stream?session_id={scan_id}&last_scanner_index={last_idx}")
        data = res.json()
        
        for log in data.get("new_scanner_logs", []):
            print(f"  > SCANNER [{log.get('level')}]: {log.get('message')}")
        
        last_idx = data.get("last_scanner_index", last_idx)
        
        if data.get("status") == "COMPLETED":
            print("Scanner finished.")
            found_count = data.get("found_count", 0)
            print(f"Found {found_count} vulnerabilities.")
            break
        
        time.sleep(1)
        poll_count += 1
        
    if found_count > 0:
        # 3. Request Auto-Queuing (Simulating frontend logic)
        print("\\n[3] Triggering Auto-Queuing...")
        res = requests.post(f"{API_URL}/confirm-automation/{scan_id}")
        if res.status_code == 200:
            print(f"Queue response: {res.json()}")
        else:
            print(f"Queue failed: {res.text}")
            sys.exit(1)
            
        # Wait a moment for queue to initialize
        time.sleep(2)
        
        # 4. Poll Pipeline Status and Logs until FIXED
        print("\\n[4] Polling Automation Pipeline & Dashboard Metrics...")
        last_auto_idx = 0
        poll_count = 0
        while poll_count < 120: # 120 seconds max for pipeline (~25s per logic block)
            # Fetch Terminal Logs
            res = requests.get(f"{API_URL}/terminal-stream?session_id={scan_id}&last_automation_index={last_auto_idx}")
            data = res.json()
            
            for log in data.get("new_automation_logs", []):
                print(f"  > AUTO KERNEL [{log.get('level')}]: {log.get('message')}")
                
            last_auto_idx = data.get("last_automation_index", last_auto_idx)
            
            # Fetch Dashboard Metrics
            dash = requests.get(f"{API_URL}/dashboard").json()
            
            fixed_count = dash.get("validated", 0)
            total_count = dash.get("total", 0)
            pending_count = dash.get("patched", 0)
            
            print(f"   [Dashboard Sync] Total: {total_count} | Pending Patch: {pending_count} | Validated (Fixed): {fixed_count}")
            
            if fixed_count >= total_count and total_count > 0:
                print(f"\\n✅ SUCCESS: All {total_count} vulnerabilities have reached FIXED state and Dashboard is completely synced.")
                break
                
            time.sleep(3)
            poll_count += 1
            
    else:
        print("No vulnerabilities found to patch.")

except Exception as e:
    print(f"Error during test: {e}")
