# 🚀 Exact Render Deployment Commands

## Copy These Exact Commands

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

## Step-by-Step Render Setup

### 1. Go to Render Dashboard
```
https://dashboard.render.com/
```

### 2. Create New Web Service
- Click **"New +"** button
- Select **"Web Service"**

### 3. Connect Repository
- Connect your GitHub account
- Select your repository
- Click **"Connect"**

### 4. Configure Service

**Name:**
```
devsecops-vulnerability-scanner
```

**Region:**
```
Oregon (US West)
```

**Branch:**
```
main
```

**Root Directory:**
```
(leave blank)
```

**Environment:**
```
Python 3
```

**Build Command:**
```
pip install -r requirements.txt
```

**Start Command:**
```
uvicorn server:app --host 0.0.0.0 --port $PORT
```

### 5. Add Environment Variable
Click **"Advanced"** → **"Add Environment Variable"**

**Key:**
```
PYTHON_VERSION
```

**Value:**
```
3.11.0
```

### 6. Set Health Check
Scroll to **"Health Check Path"**

**Value:**
```
/version
```

### 7. Select Plan
- **Free** (for testing)
- **Starter** ($7/month for production)

### 8. Deploy
Click **"Create Web Service"**

Wait 3-5 minutes for deployment to complete.

---

## Alternative Start Commands (If Needed)

### Option 1: Basic (Recommended)
```bash
uvicorn server:app --host 0.0.0.0 --port $PORT
```

### Option 2: With Workers
```bash
uvicorn server:app --host 0.0.0.0 --port $PORT --workers 2
```

### Option 3: Gunicorn
```bash
gunicorn server:app -w 2 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT
```

---

## Local Testing (Before Deploy)

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Start Server Locally
```bash
uvicorn server:app --reload --host 0.0.0.0 --port 8000
```

### Test Server
```bash
curl http://localhost:8000/version
```

### Test Workflow
```bash
python test_queue_workflow.py
```

---

## Verify Deployment

### After Render Deploys

Your app will be at:
```
https://your-app-name.onrender.com
```

### Test Endpoints
```bash
# Replace YOUR_APP_URL with your actual Render URL
export APP_URL="https://your-app-name.onrender.com"

# Test version
curl $APP_URL/version

# Test available websites
curl $APP_URL/available-websites

# Test dashboard
curl $APP_URL/dashboard
```

### Access Frontend
```
https://your-app-name.onrender.com
```

---

## Troubleshooting

### If Build Fails

**Check requirements.txt:**
```bash
cat requirements.txt
```

Should contain:
```
bandit
pydantic
typer
sqlmodel
jinja2
fastapi
uvicorn[standard]
python-multipart
regex
requests
beautifulsoup4
sqlalchemy<2.1
gunicorn
httpx
```

### If App Crashes

**Check Render Logs:**
1. Go to Render Dashboard
2. Click your service
3. Click "Logs" tab
4. Look for error messages

**Common Issues:**
- Port not set to `$PORT` → Use `--port $PORT`
- Python version mismatch → Set `PYTHON_VERSION=3.11.0`
- Missing dependencies → Check `requirements.txt`

### If App is Slow (Free Tier)

**Expected Behavior:**
- App spins down after 15 minutes of inactivity
- First request takes 30-60 seconds to wake up

**Solutions:**
- Upgrade to Starter plan ($7/month) for always-on
- Use UptimeRobot to ping every 14 minutes

---

## Files Checklist

Before deploying, ensure these files exist:

- [x] `server.py` - Main application
- [x] `requirements.txt` - Dependencies
- [x] `runtime.txt` - Python version (3.11.0)
- [x] `index.html` - Frontend
- [x] `render.yaml` - Auto-config (optional)

---

## Quick Deploy Checklist

- [ ] Push code to GitHub
- [ ] Go to Render Dashboard
- [ ] Create Web Service
- [ ] Connect repository
- [ ] Set Build Command: `pip install -r requirements.txt`
- [ ] Set Start Command: `uvicorn server:app --host 0.0.0.0 --port $PORT`
- [ ] Add Environment Variable: `PYTHON_VERSION=3.11.0`
- [ ] Set Health Check: `/version`
- [ ] Click "Create Web Service"
- [ ] Wait for deployment
- [ ] Test endpoints
- [ ] Access frontend

---

## Success Indicators

✅ Build completes without errors
✅ Service shows "Live" status
✅ Health check passes
✅ `/version` endpoint responds
✅ Frontend loads
✅ No errors in logs

---

## Support

**Render Documentation:**
https://render.com/docs

**Render Community:**
https://community.render.com/

**Status Page:**
https://status.render.com/

---

**That's it! Your app will be live in 3-5 minutes.** 🎉
