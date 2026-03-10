# Troubleshooting Guide - If Error Repeats After Deployment

## Quick Summary

The system has been fixed with 3 key changes:
1. Initialize `found_count = 0` to prevent race condition
2. Add error handling around vulnerability injection
3. Log actual errors instead of silent failures

**If issues occur after deployment, follow this guide.**

---

## Step 1: Check Render Logs

**Where:** Render Dashboard → Your Service → "Logs" tab

**Look for these error messages:**
```
[SCANNER_ENGINE] ERROR injecting simulated vulnerabilities: ...
[SCANNER_ENGINE] WARNING: Scan error for ...
[AUTOMATION_KERNEL] ERROR: Pipeline error for ...
[ERROR] Worker thread error: ...
```

---

## Step 2: Common Issues & Solutions

### Issue 1: "0 vulnerabilities detected" Message

**Symptoms:**
- Executive scan shows "Zero Vulnerabilities Found. System Secure."
- But you expect vulnerabilities to be found

**Possible Causes:**
1. Database not persisting (Render free tier resets on restart)
2. Simulated vulnerability injection failing
3. Race condition (frontend polling too early)

**Solutions:**

**A. Check if vulnerabilities are in database:**
```bash
curl https://your-app.onrender.com/vulnerabilities
```
Should return array with vulnerabilities. If empty, database is being cleared.

**B. Check Render logs for:**
```
[SCANNER_ENGINE] ERROR injecting simulated vulnerabilities: ...
```
This shows the actual error.

**C. Use PostgreSQL instead of SQLite:**
SQLite on Render free tier doesn't persist. Upgrade to PostgreSQL for production.

---

### Issue 2: Queue Processes Same Items Repeatedly

**Symptoms:**
- Same vulnerabilities appear multiple times in queue
- Automation processes same item over and over

**Possible Causes:**
1. Worker thread dying and restarting
2. Queue not clearing properly
3. Status not updating in database

**Solutions:**

**A. Check queue status:**
```bash
curl https://your-app.onrender.com/pipeline/status
```
Should show: `{"paused": false, "active": {...}, "queue": [...]}`

**B. Check Render logs for:**
```
[ERROR] Worker thread error: ...
```

**C. Restart the service:**
In Render Dashboard → Manual Deploy → Deploy Latest Commit

**D. Manually clear queue:**
```bash
curl -X POST https://your-app.onrender.com/pipeline/start
```

---

### Issue 3: Automation Doesn't Start

**Symptoms:**
- Vulnerabilities detected and queued
- Status stays at "QUEUED_FOR_PATCH"
- Nothing happens

**Possible Causes:**
1. Pipeline paused event stuck
2. Worker thread not starting
3. Queue empty

**Solutions:**

**A. Check if pipeline is paused:**
```bash
curl https://your-app.onrender.com/pipeline/status
```
If `"paused": true`, manually unpause:

**B. Manually start pipeline:**
```bash
curl -X POST https://your-app.onrender.com/pipeline/start
```

**C. Check worker is running:**
Look in logs for:
```
Worker started: True
Pipeline paused: False
```

---

### Issue 4: Frontend Shows Old Data

**Symptoms:**
- Dashboard shows wrong counts
- Vulnerabilities tab doesn't update
- Status doesn't change

**Possible Causes:**
1. Browser cache
2. Frontend polling stopped
3. Database not updating

**Solutions:**

**A. Hard refresh browser:**
- Chrome/Firefox: `Ctrl + Shift + R` (Windows) or `Cmd + Shift + R` (Mac)
- Or clear browser cache

**B. Check if backend is updating:**
```bash
curl https://your-app.onrender.com/dashboard
```
Should show current counts.

**C. Check state change timestamp:**
```bash
curl https://your-app.onrender.com/state-change-check?last_known_timestamp=0
```
Should return `{"changed": true, "timestamp": ...}`

---

## Step 3: Emergency Diagnostic Commands

### Check Server Health
```bash
# Version endpoint
curl https://your-app.onrender.com/version

# Should return: {"version": "0.1.0", "status": "operational"}
```

### Check Database
```bash
# Get all vulnerabilities
curl https://your-app.onrender.com/vulnerabilities

# Get dashboard metrics
curl https://your-app.onrender.com/dashboard

# Should show: {"total": X, "patched": Y, "validated": Z, ...}
```

### Check Queue System
```bash
# Get queue status
curl https://your-app.onrender.com/pipeline/status

# Start pipeline manually
curl -X POST https://your-app.onrender.com/pipeline/start
```

### Check Terminal Logs
```bash
# Get terminal stream
curl "https://your-app.onrender.com/terminal-stream?session_id=test&last_scanner_index=0&last_automation_index=0"

# Should return: {"new_scanner_logs": [...], "new_automation_logs": [...], "found_count": X}
```

---

## Step 4: Advanced Troubleshooting

### If Render Shell Access Available

```bash
# Check if server process is running
ps aux | grep uvicorn

# Check database file
ls -la *.db

# Check disk space
df -h

# Check memory usage
free -m

# View recent logs
tail -100 /var/log/*.log
```

### Check Environment Variables

In Render Dashboard → Environment:
- `PYTHON_VERSION` should be `3.11.0`
- No conflicting variables

---

## Step 5: Nuclear Option - Full Reset

**Only use if nothing else works!**

### Option A: Clear Build Cache
1. Render Dashboard → Your Service
2. Manual Deploy → Clear build cache
3. Deploy Latest Commit

### Option B: Force Database Reset
1. Add environment variable: `RESET_DB=true`
2. Redeploy
3. Remove the variable after first successful start

### Option C: Recreate Service
1. Delete current service in Render
2. Create new service
3. Reconnect repository
4. Use same build/start commands

---

## What Was Fixed

### Change 1: Initialize found_count (Line 870)
```python
"found_count": 0  # Prevents race condition
```
**Prevents:** Frontend seeing undefined and showing "0 vulnerabilities"

### Change 2: Error Handling for Vulnerability Injection (Lines 1077-1107)
```python
try:
    # Inject simulated vulnerabilities
except Exception as e:
    append_log(session_id, f"[SCANNER_ENGINE] ERROR injecting simulated vulnerabilities: {str(e)}", level="ERROR", log_type="scanner")
```
**Prevents:** Silent failures when injection fails

### Change 3: Better Error Logging (Lines 1199-1205)
```python
except Exception as e:
    append_log(session_id, f"[SCANNER_ENGINE] WARNING: Scan error for {app_name}: {str(e)}", level="WARNING", log_type="scanner")
```
**Prevents:** Silent failures during live scans

### Built-in Protections

1. **Queue clears before adding** (Line 897-901)
   - Prevents duplicate queueing

2. **Status check before queueing** (Line 907)
   - Only queues vulnerabilities with status="DETECTED"

3. **Worker thread safety** (Line 316)
   - Only one worker runs at a time

4. **Per-vulnerability error handling** (Line 407-415)
   - Pipeline continues even if one vulnerability fails

---

## Deployment Commands

### Build Command
```bash
pip install -r requirements.txt
```

### Start Command
```bash
uvicorn server:app --host 0.0.0.0 --port $PORT
```

### Environment Variables
```
PYTHON_VERSION=3.11.0
```

### Health Check Path
```
/version
```

---

## Expected Behavior

### Executive Scan Flow
1. User clicks "RUN EXECUTIVE PROTOCOL"
2. Scans 10 predefined websites
3. Injects 2-3 simulated vulnerabilities per site
4. Total: 20-30 vulnerabilities detected
5. Shows toast: "Scan Complete. Auto-queuing X threats..."
6. Automatically calls confirm automation

### Queue & Automation Flow
1. Vulnerabilities queued (status: DETECTED → QUEUED_FOR_PATCH)
2. Worker starts automatically
3. Processes each vulnerability:
   - QUEUED_FOR_PATCH (0s)
   - PATCH_GENERATING (5s)
   - PATCH_APPLIED (12s)
   - VALIDATING (8s)
   - FIXED or FAILED (5s)
4. Total: ~26 seconds per vulnerability
5. Dashboard updates in real-time

### Terminal Logs
```
[SCANNER_ENGINE] Starting Executive Scan
[SCANNER_ENGINE] Fetching OWASP Juice Shop
[SCANNER_ENGINE] Vulnerability detected: OWASP Juice Shop line 45
[SCANNER_ENGINE] Vulnerability detected: OWASP Juice Shop line 123
[SCANNER_ENGINE] Scan completed
[AUTOMATION_KERNEL] Queue initialized with 25 vulnerabilities
[AUTOMATION_KERNEL] Starting remediation pipeline
[AUTOMATION_KERNEL] Processing vulnerability: OWASP Juice Shop
[AUTOMATION_KERNEL] Generating patch
[AUTOMATION_KERNEL] Patch applied
[AUTOMATION_KERNEL] Validation successful
```

---

## Contact & Support

If issues persist after trying all troubleshooting steps:

1. **Check Render Status:** https://status.render.com/
2. **Review Render Logs:** Look for Python tracebacks
3. **Check Database:** Ensure SQLite file exists or use PostgreSQL
4. **Verify Environment:** Python 3.11.0, all dependencies installed

**The system is designed to show actual errors now instead of failing silently. Check logs for specific error messages.**

---

## Quick Reference

| Issue | Quick Fix |
|-------|-----------|
| 0 vulnerabilities | Check logs for injection errors |
| Queue repeating | Restart service, check worker logs |
| Automation stuck | `POST /pipeline/start` |
| Old data showing | Hard refresh browser (Ctrl+Shift+R) |
| Server not responding | Check Render logs, restart service |

**System Status: OPERATIONAL**
**Last Updated: After implementing 3 critical fixes**
