# 🚀 Deploy to Render - Quick Start

## 1️⃣ Build Command
```bash
pip install -r requirements.txt
```

## 2️⃣ Start Command
```bash
uvicorn server:app --host 0.0.0.0 --port $PORT
```

## 3️⃣ Environment Variables

### Required
| Variable | Value |
|----------|-------|
| `PYTHON_VERSION` | `3.11.0` |
| `PORT` | `8000` |

### Optional
| Variable | Value | Purpose |
|----------|-------|---------|
| `DATABASE_URL` | `sqlite:///./vulnerabilities_enforced.db` | Database path |
| `FASTAPI_ENV` | `production` | Environment mode |
| `LOG_LEVEL` | `info` | Logging level |

## 4️⃣ Health Check Path
```
/version
```

## 5️⃣ Region
```
Oregon (US West)
```

## 6️⃣ Plan
```
Free (for testing)
Starter $7/month (for production)
```

---

## Alternative Start Commands

### With Workers (Better Performance)
```bash
uvicorn server:app --host 0.0.0.0 --port $PORT --workers 2
```

### With Gunicorn
```bash
gunicorn server:app -w 2 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT
```

---

## Files Needed

✅ `requirements.txt` - Already configured
✅ `render.yaml` - Already configured (optional)
✅ `server.py` - Your main application
✅ `index.html` - Frontend

---

## After Deployment

Your app will be available at:
```
https://your-app-name.onrender.com
```

Test it:
```bash
curl https://your-app-name.onrender.com/version
```

---

## That's it! 🎉

For detailed instructions, see `RENDER_DEPLOYMENT_GUIDE.md`
