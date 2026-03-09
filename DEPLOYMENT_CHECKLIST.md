# ✅ Deployment Checklist

## Pre-Deployment

- [x] All bugfixes implemented
- [x] All tests passing
- [x] Server verified locally
- [x] requirements.txt updated
- [x] runtime.txt set to Python 3.11.0
- [x] render.yaml configured

## Render Configuration

### Copy These Values:

**Build Command:**
```
pip install -r requirements.txt
```

**Start Command:**
```
uvicorn server:app --host 0.0.0.0 --port $PORT
```

**Environment Variables:**
```
PYTHON_VERSION=3.11.0
PORT=8000
```

**Health Check Path:**
```
/version
```

## Deployment Steps

### Step 1: Push to GitHub
```bash
git add .
git commit -m "Deploy centralized automation pipeline"
git push origin main
```

### Step 2: Create Render Service
1. Go to https://dashboard.render.com/
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Select your repository

### Step 3: Configure Service
- **Name:** `devsecops-vulnerability-scanner`
- **Region:** Oregon (US West)
- **Branch:** `main`
- **Environment:** Python 3
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `uvicorn server:app --host 0.0.0.0 --port $PORT`

### Step 4: Add Environment Variables
Click "Advanced" → Add these:
- `PYTHON_VERSION` = `3.11.0`
- `PORT` = `8000`

### Step 5: Set Health Check
- **Health Check Path:** `/version`

### Step 6: Deploy
- Click "Create Web Service"
- Wait 3-5 minutes for deployment

## Post-Deployment Verification

### Step 1: Check Deployment Status
- [ ] Build completed successfully
- [ ] Service is "Live"
- [ ] No errors in logs

### Step 2: Test Endpoints
```bash
# Replace YOUR_APP_URL with your Render URL
export APP_URL="https://your-app.onrender.com"

# Test version endpoint
curl $APP_URL/version

# Test available websites
curl $APP_URL/available-websites

# Test dashboard
curl $APP_URL/dashboard
```

### Step 3: Access Frontend
- [ ] Open `https://your-app.onrender.com` in browser
- [ ] Frontend loads correctly
- [ ] All tabs visible
- [ ] No console errors

### Step 4: Test Automation Pipeline
1. [ ] Click "Executive Scan"
2. [ ] Wait for vulnerabilities to be detected
3. [ ] Scanner terminal shows logs
4. [ ] Click "Confirm Automation"
5. [ ] Automation terminal shows progress
6. [ ] Dashboard updates automatically
7. [ ] Vulnerabilities tab shows status changes
8. [ ] Patch Lab displays patches

### Step 5: Verify All Features
- [ ] Filesystem scan works
- [ ] Website scan works
- [ ] Executive scan works
- [ ] Automation queue works
- [ ] Patch generation works
- [ ] Patch validation works
- [ ] Terminal logs stream correctly
- [ ] Dashboard updates in real-time
- [ ] All modules synchronized

## Troubleshooting

### Build Fails
**Check:**
- [ ] requirements.txt is correct
- [ ] Python version is 3.11.0
- [ ] All dependencies are listed

**Fix:**
```bash
# Update requirements.txt
pip freeze > requirements.txt
git add requirements.txt
git commit -m "Update dependencies"
git push
```

### App Crashes
**Check:**
- [ ] Logs in Render dashboard
- [ ] Environment variables set correctly
- [ ] Port is $PORT (not hardcoded)

**Fix:**
- Review logs for error messages
- Verify start command uses `--port $PORT`
- Check database connection

### Slow Performance (Free Tier)
**Expected:**
- App spins down after 15 min inactivity
- First request after spin-down takes 30-60 seconds

**Solutions:**
- Upgrade to Starter plan ($7/month) for always-on
- Use UptimeRobot to ping every 14 minutes

## Monitoring

### Daily Checks
- [ ] Check service status
- [ ] Review error logs
- [ ] Monitor response times
- [ ] Check database size

### Weekly Checks
- [ ] Review usage metrics
- [ ] Check for security updates
- [ ] Test all features
- [ ] Backup database (if using PostgreSQL)

## Scaling (When Needed)

### Horizontal Scaling
Add to render.yaml:
```yaml
scaling:
  minInstances: 2
  maxInstances: 5
```

### Vertical Scaling
Upgrade plan:
- Starter: 512 MB RAM
- Standard: 2 GB RAM
- Pro: 4 GB RAM

## Security

- [ ] HTTPS enabled (automatic on Render)
- [ ] Environment variables secured
- [ ] No secrets in code
- [ ] API endpoints protected
- [ ] CORS configured correctly

## Backup Strategy

### SQLite (Free Tier)
- Database resets on each deploy
- Not recommended for production

### PostgreSQL (Recommended)
1. Add PostgreSQL database in Render
2. Set DATABASE_URL environment variable
3. Enable automatic backups
4. Test restore procedure

## Support Resources

- **Render Docs:** https://render.com/docs
- **Community:** https://community.render.com/
- **Status:** https://status.render.com/
- **Support:** support@render.com

## Success Criteria

✅ All checks passed:
- [ ] Service deployed successfully
- [ ] All endpoints responding
- [ ] Frontend accessible
- [ ] Automation pipeline working
- [ ] No errors in logs
- [ ] Performance acceptable
- [ ] All features functional

## Next Steps After Deployment

1. [ ] Share URL with team
2. [ ] Set up monitoring alerts
3. [ ] Configure custom domain (optional)
4. [ ] Enable automatic backups
5. [ ] Document any custom configurations
6. [ ] Plan for scaling if needed

---

**Deployment Status:** 🟢 READY TO DEPLOY

**Estimated Time:** 10-15 minutes

**Difficulty:** Easy ⭐

---

## Quick Reference

**Your Render URL will be:**
```
https://devsecops-vulnerability-scanner.onrender.com
```

**To redeploy:**
```bash
git push origin main
```
(Render auto-deploys on push)

**To view logs:**
- Render Dashboard → Your Service → Logs

**To update environment variables:**
- Render Dashboard → Your Service → Environment

---

**Ready to deploy? Follow the steps above!** 🚀
