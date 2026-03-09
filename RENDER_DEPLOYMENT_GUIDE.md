# 🚀 Render Deployment Guide

## Quick Deploy to Render

### Method 1: Using render.yaml (Recommended)

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Add centralized automation pipeline"
   git push origin main
   ```

2. **Connect to Render**
   - Go to [Render Dashboard](https://dashboard.render.com/)
   - Click "New +" → "Blueprint"
   - Connect your GitHub repository
   - Render will automatically detect `render.yaml`
   - Click "Apply"

### Method 2: Manual Setup

1. **Create New Web Service**
   - Go to [Render Dashboard](https://dashboard.render.com/)
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Select your repository

2. **Configure Build Settings**

   **Name:** `devsecops-vulnerability-scanner`
   
   **Region:** Oregon (US West) or closest to you
   
   **Branch:** `main`
   
   **Root Directory:** Leave blank (or `.` if needed)
   
   **Environment:** `Python 3`
   
   **Build Command:**
   ```bash
   pip install -r requirements.txt
   ```
   
   **Start Command:**
   ```bash
   uvicorn server:app --host 0.0.0.0 --port $PORT
   ```

3. **Environment Variables**

   Click "Advanced" → "Add Environment Variable"

   | Key | Value | Description |
   |-----|-------|-------------|
   | `PYTHON_VERSION` | `3.11.0` | Python version (3.11 recommended) |
   | `PORT` | `8000` | Port (Render sets this automatically) |

   **Optional Environment Variables:**

   | Key | Value | Description |
   |-----|-------|-------------|
   | `DATABASE_URL` | `sqlite:///./vulnerabilities_enforced.db` | Database path |
   | `FASTAPI_ENV` | `production` | Environment mode |
   | `LOG_LEVEL` | `info` | Logging level |

4. **Health Check Path**
   ```
   /version
   ```

5. **Plan**
   - Select "Free" for testing
   - Upgrade to "Starter" ($7/month) for production

6. **Click "Create Web Service"**

## Build Configuration Files

### requirements.txt
```txt
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

### render.yaml (Auto-detected)
```yaml
services:
  - type: web
    name: devsecops-vulnerability-scanner
    env: python
    region: oregon
    plan: free
    branch: main
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn server:app --host 0.0.0.0 --port $PORT
    healthCheckPath: /version
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0
      - key: PORT
        value: 8000
```

## Alternative Start Commands

### Option 1: Uvicorn (Recommended)
```bash
uvicorn server:app --host 0.0.0.0 --port $PORT
```

### Option 2: Uvicorn with Workers
```bash
uvicorn server:app --host 0.0.0.0 --port $PORT --workers 2
```

### Option 3: Gunicorn with Uvicorn Workers
```bash
gunicorn server:app -w 2 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT
```

## Database Configuration

### SQLite (Default - Free Tier)
The app uses SQLite by default. Database file will be created automatically:
```
vulnerabilities_enforced.db
```

**Note:** On Render's free tier, the database will reset on each deploy. For persistent data, upgrade to a paid plan or use PostgreSQL.

### PostgreSQL (Production - Recommended)

1. **Add PostgreSQL Database**
   - In Render Dashboard → "New +" → "PostgreSQL"
   - Name: `devsecops-db`
   - Plan: Free or Starter
   - Click "Create Database"

2. **Update Environment Variables**
   - Copy the "Internal Database URL"
   - Add to your web service:
   ```
   DATABASE_URL=postgresql://user:pass@host/dbname
   ```

3. **Update server.py** (if needed)
   ```python
   DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DB_PATH}")
   ```

## Post-Deployment Steps

### 1. Verify Deployment
Once deployed, Render will provide a URL like:
```
https://devsecops-vulnerability-scanner.onrender.com
```

### 2. Test Endpoints
```bash
# Check version
curl https://your-app.onrender.com/version

# Check health
curl https://your-app.onrender.com/

# Check available websites
curl https://your-app.onrender.com/available-websites
```

### 3. Access Frontend
Open in browser:
```
https://your-app.onrender.com
```

### 4. Run Migration (if needed)
If you have existing data to migrate:
```bash
# SSH into Render shell (paid plans only)
python migrate_unified_schema.py
```

## Troubleshooting

### Build Fails

**Issue:** `ModuleNotFoundError`
**Solution:** Ensure all dependencies are in `requirements.txt`

**Issue:** Python version mismatch
**Solution:** Set `PYTHON_VERSION=3.11.0` in environment variables

### App Crashes on Start

**Issue:** Port binding error
**Solution:** Use `--host 0.0.0.0 --port $PORT` (Render sets PORT automatically)

**Issue:** Database connection error
**Solution:** Check `DATABASE_URL` environment variable

### Slow Cold Starts (Free Tier)

**Issue:** App spins down after 15 minutes of inactivity
**Solution:** 
- Upgrade to paid plan for always-on
- Or use a service like UptimeRobot to ping every 14 minutes

### Database Resets on Deploy

**Issue:** SQLite database resets on each deploy
**Solution:** 
- Use PostgreSQL for persistent storage
- Or upgrade to paid plan with persistent disk

## Monitoring

### Logs
View logs in Render Dashboard:
- Click your service
- Go to "Logs" tab
- Real-time log streaming

### Metrics
- CPU usage
- Memory usage
- Request count
- Response times

## Custom Domain (Optional)

1. Go to your service → "Settings"
2. Scroll to "Custom Domain"
3. Click "Add Custom Domain"
4. Follow DNS configuration instructions

## Scaling (Paid Plans)

### Horizontal Scaling
```yaml
services:
  - type: web
    scaling:
      minInstances: 2
      maxInstances: 5
```

### Vertical Scaling
Upgrade plan:
- Starter: 512 MB RAM
- Standard: 2 GB RAM
- Pro: 4 GB RAM

## Security Best Practices

1. **Environment Variables**
   - Never commit secrets to Git
   - Use Render's environment variables

2. **HTTPS**
   - Render provides free SSL certificates
   - All traffic is encrypted

3. **API Keys**
   - Store in environment variables
   - Rotate regularly

## Cost Estimate

### Free Tier
- ✅ 750 hours/month
- ✅ Automatic SSL
- ✅ Continuous deployment
- ⚠️ Spins down after 15 min inactivity
- ⚠️ No persistent disk

### Starter ($7/month)
- ✅ Always on
- ✅ Persistent disk
- ✅ More resources
- ✅ Better performance

## Support

- [Render Documentation](https://render.com/docs)
- [Render Community](https://community.render.com/)
- [Status Page](https://status.render.com/)

## Quick Commands Reference

```bash
# Local testing
uvicorn server:app --reload --host 0.0.0.0 --port 8000

# Check dependencies
pip freeze > requirements.txt

# Test build locally
pip install -r requirements.txt

# Run tests
python -m pytest test_full_automation.py -v

# Check server
python -c "from server import app; print('Server ready')"
```

## Deployment Checklist

- [ ] Push code to GitHub
- [ ] Create Render account
- [ ] Connect GitHub repository
- [ ] Configure build settings
- [ ] Set environment variables
- [ ] Deploy service
- [ ] Verify deployment
- [ ] Test endpoints
- [ ] Access frontend
- [ ] Monitor logs
- [ ] Set up custom domain (optional)

## Next Steps After Deployment

1. ✅ Test executive scan workflow
2. ✅ Verify automation pipeline
3. ✅ Check dashboard updates
4. ✅ Monitor terminal logs
5. ✅ Test error recovery
6. ✅ Verify all modules synchronized

---

**Your app is now live and ready for production!** 🎉
