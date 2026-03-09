import requests
import time

BASE_URL = "http://localhost:8000"

def wait_for_server():
    print("Waiting for server to start...")
    for _ in range(15):
        try:
            requests.get(f"{BASE_URL}/")
            return True
        except requests.exceptions.ConnectionError:
            time.sleep(1)
    return False

def test_controlled_queue():
    if not wait_for_server():
        print("Server failed to start.")
        return
        
    print("\n--- 1. START EXECUTIVE SCAN ---")
    resp = requests.post(f"{BASE_URL}/executive-scan").json()
    scan_id = resp["scan_id"]
    print(f"Started scan ID: {scan_id}")
    
    print("\n--- 2. WAIT FOR COMPLETION AND CHECK LOGS ---")
    # Poll until completed
    status = "RUNNING"
    last_scanner_idx = 0
    last_auto_idx = 0
    
    while status == "RUNNING":
        time.sleep(2)
        stream = requests.get(f"{BASE_URL}/terminal-stream", params={
            "session_id": scan_id, 
            "last_scanner_index": last_scanner_idx,
            "last_automation_index": last_auto_idx
        }).json()
        
        status = stream["status"]
        for msg in stream["new_scanner_logs"]:
            print(msg["message"])
        last_scanner_idx = stream["last_scanner_index"]
        last_auto_idx = stream["last_automation_index"]
    
    print("\n--- 3. VERIFY AUTO-QUEUE DID NOT START ---")
    q_status = requests.get(f"{BASE_URL}/queue-status").json()
    if q_status["active_scan"] is None and len(q_status["pending_jobs"]) == 0:
         print("SUCCESS: Pipeline is paused. No jobs are queued automatically.")
    else:
         print("ERROR: Jobs started automatically!")
    
    print("\n--- 4. SIMULATE USER CONFIRMATION (/confirm-automation) ---")
    conf_resp = requests.post(f"{BASE_URL}/confirm-automation/{scan_id}")
    if conf_resp.status_code == 200:
        print(f"Confirmed successfully: {conf_resp.json()}")
    else:
        print(f"Error confirming: {conf_resp.text}")
        return
        
    print("\n--- 5. CHECK AUTOMATION LOGS ---")
    for _ in range(10):
        time.sleep(2)
        stream = requests.get(f"{BASE_URL}/terminal-stream", params={
            "session_id": scan_id, 
            "last_scanner_index": last_scanner_idx,
            "last_automation_index": last_auto_idx
        }).json()
        
        for msg in stream["new_automation_logs"]:
            print(msg["message"])
        last_auto_idx = stream["last_automation_index"]

if __name__ == "__main__":
    test_controlled_queue()
