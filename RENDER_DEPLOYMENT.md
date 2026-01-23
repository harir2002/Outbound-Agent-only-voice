# 🚀 Render Deployment Guide - BFSI AI Platform

## ⚠️ Problem: Deployment Timeout

Your original deployment was timing out because of **massive dependencies**:
- PyTorch: 915 MB
- CUDA libraries: 2+ GB
- Total build time: 10+ minutes
- Startup time: Too slow for Render's free tier health checks

## ✅ Solution: Lightweight Production Build

### What We Changed:

1. **Created `requirements.prod.txt`** - Removed heavy ML dependencies:
   - ❌ Removed: `sentence-transformers` (pulls PyTorch + CUDA)
   - ❌ Removed: `chromadb` (requires heavy ML models)
   - ❌ Removed: `pandas` (not needed for production)
   - ✅ Kept: All core functionality (Groq, Twilio, FastAPI, etc.)

2. **Created `Dockerfile.prod`** - Optimized container:
   - Uses lightweight Python 3.11-slim
   - Health checks configured
   - Proper timeout settings
   - Minimal system dependencies

3. **Updated `render.yaml`**:
   - Added health check path
   - Uses production Dockerfile
   - Correct port configuration (10000)

### Deployment Steps:

#### 1. Commit Changes
```bash
cd "c:\Users\HARI R\Desktop\Sales Application and Demo\Outbound Whatsapp Demo"
git add .
git commit -m "Deploy: Lightweight production build for Render"
git push origin main
```

#### 2. Configure Environment Variables in Render Dashboard

Go to your Render service settings and add these **required** environment variables:

**Essential API Keys:**
- `GROQ_API_KEY` - Your Groq API key
- `SARVAM_API_KEY` - Your Sarvam AI key
- `TWILIO_ACCOUNT_SID` - Twilio account SID
- `TWILIO_AUTH_TOKEN` - Twilio auth token
- `TWILIO_PHONE_NUMBER` - Your Twilio phone number
- `TWILIO_WHATSAPP_NUMBER` - Your Twilio WhatsApp number

**Database (Auto-configured from render.yaml):**
- `DATABASE_URL` - Will be auto-populated from bfsi-db

**Optional:**
- `CORS_ORIGINS` - Frontend URLs (comma-separated)
  Example: `https://your-frontend.onrender.com,http://localhost:5173`
- `REDIS_URL` - If you add Redis service later
- `SENTRY_DSN` - For error monitoring (optional)

#### 3. Deploy

Render will automatically deploy when you push to your repo.

**Expected timeline:**
- ✅ Build: 3-5 minutes (instead of 10+)
- ✅ Deploy: 30-60 seconds
- ✅ Total: ~5 minutes

#### 4. Verify Deployment

Once deployed, test these endpoints:

1. **Health Check:**
   ```
   https://bfsi-backend.onrender.com/health
   ```
   Should return: `{"status":"healthy",...}`

2. **API Docs:**
   ```
   https://bfsi-backend.onrender.com/docs
   ```

3. **Root:**
   ```
   https://bfsi-backend.onrender.com/
   ```

### Monitoring

Watch the deployment logs in Render dashboard for:
- ✅ "Starting BFSI AI Platform..."
- ✅ "All services initialized successfully"
- ✅ Health checks passing

### Troubleshooting

#### If Still Timing Out:

1. **Check Logs** - Look for error messages during startup
2. **Verify Database** - Ensure `bfsi-db` is running
3. **Check Environment Variables** - All required vars set?
4. **Health Check** - Is `/health` endpoint responding?

#### Common Issues:

**Issue:** "Port already in use"
- **Fix:** Render automatically sets `PORT=10000` env var

**Issue:** "Database connection failed"
- **Fix:** Ensure `DATABASE_URL` is set from render.yaml

**Issue:** "Module not found"
- **Fix:** Check `requirements.prod.txt` includes all needed packages

### What Features Still Work:

✅ **All Core Features:**
- Groq LLM for AI responses
- Twilio Voice & WhatsApp
- SMS campaigns
- PostgreSQL database
- Analytics
- Authentication
- Logging

❌ **Temporarily Disabled (too heavy for free tier):**
- ChromaDB vector search
- Sentence transformers embeddings

### Upgrade Path (Paid Tier):

If you upgrade to Render paid tier ($7/month), you can:
1. Switch back to full `requirements.txt`
2. Use original `Dockerfile`
3. Enable ChromaDB and ML features
4. Increase memory/CPU limits

### Performance Optimization:

The lightweight build is actually **better for production** because:
- ✅ Faster deployments
- ✅ Lower memory usage
- ✅ Quicker cold starts
- ✅ Better for serverless architecture

You're using **Groq's cloud LLM** anyway, so local ML models aren't needed!

---

## 📝 Quick Reference

**Files Modified:**
- ✅ `render.yaml` - Added health checks
- ✅ `requirements.prod.txt` - Lightweight dependencies
- ✅ `Dockerfile.prod` - Optimized container

**Files Unchanged:**
- ✅ All application code works as-is
- ✅ No code changes needed in `app/`

**Next Steps:**
1. Push to GitHub
2. Wait for Render auto-deploy
3. Test endpoints
4. Update frontend with backend URL
