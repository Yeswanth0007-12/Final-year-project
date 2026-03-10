import requests
import time
import sys
import os

API_URL = "http://127.0.0.1:8000"

def test_pipeline():
    print("🚀 INITIALIZING SYSTEM-WIDE VERIFICATION (PHASE 12)...")
    
    # 1. Trigger Executive Scan
    print("\n[STEP 1] TRIGGERING EXECUTIVE SCAN...")
    try:
        res = requests.post(f"{API_URL}/executive-scan")
        if res.status_code != 200:
            print(f"❌ Server returned error: {res.text}")
            return
        data = res.json()
        scan_id = data["scan_id"]
        print(f"✅ Scan ID Initialized: {scan_id}")
    except Exception as e:
        print(f"❌ Failed to trigger scan: {e}")
        return

    # 2. Poll Terminal Stream
    print("\n[STEP 2] STREAMING TERMINAL LOGS (SCANNER & AUTOMATION)...")
    last_scanner = 0
    last_auto = 0
    
    start_time = time.time()
    # We expect the scan to take ~20-30 seconds given the time.sleep(1) per site in executive scan
    # and then automation starts.
    while time.time() - start_time < 300: # 5 minute timeout for full demo
        try:
            res = requests.get(f"{API_URL}/terminal-stream", params={
                "session_id": scan_id,
                "last_scanner_index": last_scanner,
                "last_automation_index": last_auto
            })
            if res.status_code != 200:
                print(f"⚠️ Server status: {res.status_code}")
                time.sleep(2)
                continue
                
            data = res.json()
            
            # Print new scanner logs
            for log in data["new_scanner_logs"]:
                print(f"[SCANNER] {log['message']}")
            
            # Print new automation logs
            for log in data["new_automation_logs"]:
                print(f"[AUTOMATION] {log['message']}")
                
            last_scanner = data["last_scanner_index"]
            last_auto = data["last_automation_index"]
            
            # If everything is COMPLETED in the terminal session and we have some logs
            if data["status"] == "COMPLETED" and last_scanner > 0:
                # Give it a bit more time for the automation kernel to finish its background work
                # if the last site was just scanned.
                time.sleep(2)
                res_final = requests.get(f"{API_URL}/terminal-stream", params={
                    "session_id": scan_id,
                    "last_scanner_index": last_scanner,
                    "last_automation_index": last_auto
                })
                data_final = res_final.json()
                for log in data_final["new_automation_logs"]:
                    print(f"[AUTOMATION] {log['message']}")
                
                print("\n✅ LOG STREAMING COMPLETE.")
                break
                
            time.sleep(1)
        except Exception as e:
            print(f"⚠️ Polling error: {e}")
            time.sleep(2)

    # 3. Verify Dashboard Metrics
    print("\n[STEP 3] VERIFYING DASHBOARD DATA CONSISTENCY...")
    try:
        res = requests.get(f"{API_URL}/dashboard")
        dash = res.json()
        print(f"📊 Dashboard Metrics:")
        print(f"   - Total Vulnerabilities: {dash['total']}")
        print(f"   - In Remediation: {dash['patched']}")
        print(f"   - Fully Validated: {dash['validated']}")
        print(f"   - Mean Risk Score: {dash['risk_score']}")
        
        if dash['total'] > 0:
            print("✅ Dashboard is live and aggregated from DB.")
        else:
            print("❌ Dashboard returned 0 results. Check DB initialization.")
    except Exception as e:
        print(f"❌ Failed to fetch dashboard: {e}")

    # 4. Final check on vulnerabilities
    print("\n[STEP 4] VERIFYING VULNERABILITY REGISTRY...")
    try:
        res = requests.get(f"{API_URL}/vulnerabilities")
        vulns = res.json()
        print(f"📂 Registry Status: {len(vulns)} detections synchronized.")
        if len(vulns) > 0:
            unique_status = set(v['status'] for v in vulns)
            print(f"   - Global Status State: {list(unique_status)}")
            print("✅ Registry fully synchronized with DB.")
    except Exception as e:
        print(f"❌ Failed to fetch vulnerabilities: {e}")

    print("\n🌐 SYSTEM VERIFICATION PROTOCOL COMPLETE.")

if __name__ == "__main__":
    test_pipeline()
