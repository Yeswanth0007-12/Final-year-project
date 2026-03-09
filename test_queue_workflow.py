"""
Test Queue Workflow
Tests the two-step confirmation process for queue and automation
"""
import requests
import time
import json

BASE_URL = "http://localhost:8000"

def test_workflow():
    print("=" * 60)
    print("TESTING QUEUE WORKFLOW")
    print("=" * 60)
    
    # Step 1: Start Executive Scan
    print("\n1. Starting Executive Scan...")
    response = requests.post(f"{BASE_URL}/executive-scan")
    assert response.status_code == 200, f"Executive scan failed: {response.text}"
    
    scan_data = response.json()
    scan_id = scan_data["scan_id"]
    print(f"   ✓ Scan started: {scan_id}")
    
    # Wait for scan to complete
    print("\n2. Waiting for scan to complete...")
    time.sleep(10)
    
    # Check terminal logs
    response = requests.get(f"{BASE_URL}/terminal-stream/{scan_id}")
    terminal_data = response.json()
    scanner_logs = terminal_data.get("new_scanner_logs", [])
    print(f"   ✓ Scanner logs: {len(scanner_logs)} entries")
    
    # Step 2: Queue Vulnerabilities (First Confirmation)
    print("\n3. Queueing vulnerabilities (First Confirmation)...")
    response = requests.post(f"{BASE_URL}/queue-vulnerabilities/{scan_id}")
    
    if response.status_code == 200:
        queue_data = response.json()
        print(f"   ✓ {queue_data['message']}")
        print(f"   ✓ Queue size: {queue_data['queue_size']}")
    else:
        print(f"   ✗ Queue failed: {response.text}")
        return
    
    # Check automation logs after queuing
    time.sleep(2)
    response = requests.get(f"{BASE_URL}/terminal-stream/{scan_id}")
    terminal_data = response.json()
    automation_logs = terminal_data.get("new_automation_logs", [])
    print(f"   ✓ Automation logs: {len(automation_logs)} entries")
    
    # Print some automation logs
    for log in automation_logs[:5]:
        print(f"      [{log['level']}] {log['message']}")
    
    # Step 3: Start Automation (Second Confirmation)
    print("\n4. Starting automation (Second Confirmation)...")
    response = requests.post(f"{BASE_URL}/start-automation/{scan_id}")
    
    if response.status_code == 200:
        auto_data = response.json()
        print(f"   ✓ {auto_data['message']}")
        print(f"   ✓ Processing {auto_data['queue_size']} vulnerabilities")
    else:
        print(f"   ✗ Automation start failed: {response.text}")
        return
    
    # Monitor automation progress
    print("\n5. Monitoring automation progress...")
    for i in range(10):
        time.sleep(5)
        
        # Get terminal logs
        response = requests.get(f"{BASE_URL}/terminal-stream/{scan_id}")
        terminal_data = response.json()
        automation_logs = terminal_data.get("new_automation_logs", [])
        
        # Get vulnerabilities status
        response = requests.get(f"{BASE_URL}/vulnerabilities")
        vulns = response.json()
        
        status_counts = {}
        for v in vulns:
            status = v.get("status", "UNKNOWN")
            status_counts[status] = status_counts.get(status, 0) + 1
        
        print(f"\n   Iteration {i+1}:")
        print(f"   - Automation logs: {len(automation_logs)} total")
        print(f"   - Status counts: {status_counts}")
        
        # Show recent logs
        if automation_logs:
            recent = automation_logs[-3:]
            for log in recent:
                print(f"      [{log['level']}] {log['message']}")
        
        # Check if all done
        if status_counts.get("FIXED", 0) + status_counts.get("FAILED", 0) == sum(status_counts.values()):
            print("\n   ✓ All vulnerabilities processed!")
            break
    
    # Final status
    print("\n6. Final Status:")
    response = requests.get(f"{BASE_URL}/vulnerabilities")
    vulns = response.json()
    
    for v in vulns[:5]:  # Show first 5
        print(f"   - {v['website_name']}: {v['vulnerability_type']} → {v['status']}")
    
    print("\n" + "=" * 60)
    print("WORKFLOW TEST COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    try:
        test_workflow()
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
