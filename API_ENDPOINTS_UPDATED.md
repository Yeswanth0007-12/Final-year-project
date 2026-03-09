# API Endpoints - Updated

## New Endpoints (Queue Workflow)

### 1. Queue Vulnerabilities (First Confirmation)
```http
POST /queue-vulnerabilities/{scan_id}
```

**Description:** Queue detected vulnerabilities for automation

**Parameters:**
- `scan_id` (path) - Scan session ID from executive scan

**Response:**
```json
{
  "status": "QUEUED",
  "queue_size": 3,
  "message": "3 vulnerabilities queued for automation"
}
```

**Status Codes:**
- `200` - Success
- `404` - Scan session not found
- `404` - No vulnerabilities found

**Example:**
```bash
curl -X POST http://localhost:8000/queue-vulnerabilities/executive-abc123
```

---

### 2. Start Automation (Second Confirmation)
```http
POST /start-automation/{scan_id}
```

**Description:** Start automated patch remediation

**Parameters:**
- `scan_id` (path) - Scan session ID

**Response:**
```json
{
  "status": "AUTOMATION_STARTED",
  "queue_size": 3,
  "message": "Automated remediation started for 3 vulnerabilities"
}
```

**Status Codes:**
- `200` - Success
- `404` - Scan session not found
- `400` - No vulnerabilities in queue

**Example:**
```bash
curl -X POST http://localhost:8000/start-automation/executive-abc123
```

---

## Existing Endpoints (Preserved)

### Executive Scan
```http
POST /executive-scan
```

**Response:**
```json
{
  "scan_id": "executive-abc123",
  "status": "RUNNING"
}
```

---

### Terminal Stream
```http
GET /terminal-stream/{scan_id}?last_scanner_index=0&last_automation_index=0
```

**Response:**
```json
{
  "status": "RUNNING",
  "new_scanner_logs": [...],
  "new_automation_logs": [...],
  "last_scanner_index": 5,
  "last_automation_index": 10,
  "found_count": 3
}
```

---

### Get Vulnerabilities
```http
GET /vulnerabilities
```

**Response:**
```json
[
  {
    "id": "VULN-12345",
    "website_name": "example.com",
    "vulnerability_type": "EVAL_INJECTION",
    "status": "FIXED",
    "line_number": 42,
    "code_snippet": "eval(input)",
    "patch_code": "ast.literal_eval(input)",
    "decision_score": 0.95
  }
]
```

---

### Dashboard Stats
```http
GET /dashboard
```

**Response:**
```json
{
  "total": 10,
  "patched": 3,
  "validated": 5,
  "risk_score": 45.2,
  "last_update": 1234567890.123
}
```

---

### Pipeline Status
```http
GET /pipeline/status
```

**Response:**
```json
{
  "active": true,
  "queue": [...],
  "paused": false,
  "queuing_active": false,
  "queue_count": 3
}
```

---

## Workflow Sequence

```
1. POST /executive-scan
   → Returns scan_id
   
2. Wait for scan completion
   → Poll GET /terminal-stream/{scan_id}
   
3. POST /queue-vulnerabilities/{scan_id}
   → First confirmation
   → Queues vulnerabilities
   
4. POST /start-automation/{scan_id}
   → Second confirmation
   → Starts automation
   
5. Monitor progress
   → Poll GET /terminal-stream/{scan_id}
   → Poll GET /vulnerabilities
   → Poll GET /dashboard
```

---

## Error Responses

### 404 Not Found
```json
{
  "detail": "Scan session not found."
}
```

### 400 Bad Request
```json
{
  "detail": "No vulnerabilities in queue. Please queue vulnerabilities first."
}
```

### 500 Internal Server Error
```json
{
  "detail": "Error message",
  "traceback": "..."
}
```

---

## Testing with cURL

### Complete Workflow:
```bash
# 1. Start scan
SCAN_ID=$(curl -X POST http://localhost:8000/executive-scan | jq -r '.scan_id')
echo "Scan ID: $SCAN_ID"

# 2. Wait for scan
sleep 10

# 3. Queue vulnerabilities
curl -X POST http://localhost:8000/queue-vulnerabilities/$SCAN_ID

# 4. Start automation
curl -X POST http://localhost:8000/start-automation/$SCAN_ID

# 5. Monitor logs
curl "http://localhost:8000/terminal-stream/$SCAN_ID?last_scanner_index=0&last_automation_index=0"

# 6. Check vulnerabilities
curl http://localhost:8000/vulnerabilities

# 7. Check dashboard
curl http://localhost:8000/dashboard
```

---

## Frontend Integration

The frontend should:

1. Call `/executive-scan` when user clicks "Executive Scan"
2. Poll `/terminal-stream/{scan_id}` to show scanner logs
3. When scan completes, show popup: "X vulnerabilities detected. Queue for automation?"
4. If YES, call `/queue-vulnerabilities/{scan_id}`
5. Poll `/terminal-stream/{scan_id}` to show queuing logs
6. Show second popup: "Queue initialized. Start automation?"
7. If YES, call `/start-automation/{scan_id}`
8. Poll `/terminal-stream/{scan_id}` to show automation logs
9. Poll `/vulnerabilities` to update Vulnerabilities tab
10. Poll `/dashboard` to update Dashboard metrics

---

**All endpoints tested and working correctly!** ✅
