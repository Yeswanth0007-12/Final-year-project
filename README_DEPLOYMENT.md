# 🚀 Render Deployment - Complete Guide

## Quick Start (Copy & Paste)

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
PORT=8000
```

### Health Check Path
```
/version
```

---

## Detailed Configuration

### 1. Service Settings
| Setting | Value |
|---------|-------|
| **Name** | `devsecops-vulnerability-scanner` |
| **Environment** | Python 3 |
| **Region** | Oregon (US West) |
| **Branch** | `main` |
| **Plan** | Free (or Starter $7/month) |

### 2. Build Settings
| Setting | Value |
|---------|-------|
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `uvicorn server:app --host 0.0.0.0 --port $PORT` |
| **Health Check** | `/version` |

### 3. Environment Variables (Required)
```env
PYTHON_VERSION=3.11.0
PORT=8000
```

### 4. Environment Variables (Optional)
```env
DATABASE_URL=sqlite:///./vulnerabilities_enforced.db
FASTAPI_ENV=production
LOG_LEVEL=info
```

---

## Alternative Start Commands

### Option 1: Basic (Recommended for Free Tier)
```bash
uvicorn server:app --host 0.0.0.0 --port $PORT
```

### Option 2: With Workers (Better Performance)
```bash
uvicorn server:app --host 0.0.0.0 --port $PORT --workers 2
```

### Option 3: Gunicorn (Production)
```bash
gunicorn server:app -w 2 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT
```

---

## Deployment Methods

### Method 1: Using render.yaml (Automatic)
1. Push code to GitHub
2. Go to Render Dashboard
3. Click "New +" → "Blueprint"
4. Connect repository
5. Render auto-detects `render.yaml`
6. Click "Apply"

### Method 2: Manual Setup
1. Go to Render Dashboard
2. Click "New +" → "Web Service"
3. Connect repository
4. Enter configuration above
5. Click "Create Web Service"

---

## Files Included

✅ **requirements.txt** - All Python dependencies
✅ **runtime.txt** - Python 3.11.0
✅ **render.yaml** - Auto-deployment config
✅ **server.py** - Main application
✅ **index.html** - Frontend UI
✅ **pipeline_manager.py** - Pipeline orchestrator
✅ **scan_engine/** - Vulnerability scanner

---

## After Deployment

### Your App URL
```
https://your-app-name.onrender.com
```

### Test Endpoints
```bash
# Check version
curl https://your-app.onrender.com/version

# Check available websites
curl https://your-app.onrender.com/available-websites

# Check dashboard
curl https://your-app.onrender.com/dashboard
```

### Access Frontend
```
https://your-app.onrender.com
```

---

## Features Deployed

✅ **Unified Database Schema** - Single source of truth
✅ **Thread-Safe Queue** - No race conditions
✅ **Incremental Logs** - Smooth streaming
✅ **Auto Updates** - Real-time dashboard
✅ **Pipeline Orchestrator** - Centralized control
✅ **Error Recovery** - Robust handling
✅ **Full Automation** - Hands-free operation

---

## Troubleshooting

### Build Fails
- Check `requirements.txt` is complete
- Verify Python version is 3.11.0
- Review build logs in Render

### App Crashes
- Check logs in Render dashboard
- Verify environment variables
- Ensure start command uses `$PORT`

### Slow Cold Starts (Free Tier)
- Expected: App spins down after 15 min
- Solution: Upgrade to Starter plan

---

## Cost

### Free Tier
- ✅ 750 hours/month
- ✅ Automatic SSL
- ✅ Continuous deployment
- ⚠️ Spins down after 15 min
- ⚠️ No persistent disk

### Starter ($7/month)
- ✅ Always on
- ✅ Persistent disk
- ✅ Better performance
- ✅ More resources

---

## Documentation Files

📄 **DEPLOY_QUICK_START.md** - Quick reference
📄 **RENDER_DEPLOYMENT_GUIDE.md** - Detailed guide
📄 **DEPLOYMENT_CHECKLIST.md** - Step-by-step checklist
📄 **RENDER_CONFIG_SUMMARY.txt** - Visual summary
📄 **BUGFIX_COMPLETE.md** - Implementation details
📄 **IMPLEMENTATION_SUMMARY.md** - Technical details

---

## Support

- **Render Docs:** https://render.com/docs
- **Community:** https://community.render.com/
- **Status:** https://status.render.com/

---

## Quick Commands

```bash
# Local testing
uvicorn server:app --reload --host 0.0.0.0 --port 8000

# Run tests
python -m pytest test_full_automation.py -v

# Check server
python -c "from server import app; print('Server ready')"

# Push to deploy
git add .
git commit -m "Deploy"
git push origin main
```

---

## Success Checklist

- [ ] Code pushed to GitHub
- [ ] Render service created
- [ ] Build completed
- [ ] Service is live
- [ ] Endpoints responding
- [ ] Frontend accessible
- [ ] Automation working
- [ ] No errors in logs

---

**🎉 Your app is ready to deploy!**

**Estimated deployment time:** 10-15 minutes

**Need help?** Check the detailed guides in the documentation files above.
