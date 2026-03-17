# Deployment Guide

This guide will help you deploy the Syllabus Calendar Extractor to the web using Railway (backend) and Vercel (frontend).

## Prerequisites

- GitHub account
- Railway account (https://railway.app - sign up with GitHub)
- Vercel account (https://vercel.com - sign up with GitHub)

## Step 1: Push Code to GitHub

1. Initialize git repository (if not already done):
```bash
cd /Users/bhavikaagoenka/syllabus-calendar-app
git init
git add .
git commit -m "Initial commit - Syllabus Calendar App"
```

2. Create a new repository on GitHub:
   - Go to https://github.com/new
   - Name it: `syllabus-calendar-app`
   - Don't initialize with README (we already have code)
   - Click "Create repository"

3. Push your code:
```bash
git remote add origin https://github.com/YOUR_USERNAME/syllabus-calendar-app.git
git branch -M main
git push -u origin main
```

## Step 2: Deploy Backend to Railway

1. Go to https://railway.app and sign in with GitHub

2. Click "New Project"

3. Select "Deploy from GitHub repo"

4. Select your `syllabus-calendar-app` repository

5. Railway will detect the backend automatically. Configure:
   - **Root Directory**: `/backend`
   - **Build Command**: (Auto-detected)
   - **Start Command**: `gunicorn app:app`

6. Click "Deploy"

7. Once deployed, go to "Settings" tab:
   - Click "Generate Domain" to get a public URL
   - Copy this URL (e.g., `https://your-app.railway.app`)

8. (Optional) Add environment variables:
   - Go to "Variables" tab
   - Add `ANTHROPIC_API_KEY` if you want server-side AI support

## Step 3: Deploy Frontend to Vercel

1. Go to https://vercel.com and sign in with GitHub

2. Click "Add New" → "Project"

3. Import your `syllabus-calendar-app` repository

4. Configure the project:
   - **Framework Preset**: Create React App
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `build`

5. Add Environment Variable:
   - Click "Environment Variables"
   - Add variable:
     - **Name**: `REACT_APP_API_URL`
     - **Value**: `https://your-app.railway.app` (your Railway backend URL from Step 2)
   - Select all environments (Production, Preview, Development)

6. Click "Deploy"

7. Wait for deployment to complete (1-2 minutes)

8. Vercel will provide your live URL (e.g., `https://your-app.vercel.app`)

## Step 4: Update Backend CORS (if needed)

If you get CORS errors, update the backend:

1. In Railway dashboard, go to your backend project

2. Add environment variable:
   - **Name**: `ALLOWED_ORIGINS`
   - **Value**: `https://your-app.vercel.app`

3. The backend is already configured to accept all origins for `/api/*` routes, so this should work without changes

## Step 5: Test Your Deployment

1. Visit your Vercel URL (e.g., `https://your-app.vercel.app`)

2. Try uploading a sample syllabus:
   - Set semester dates
   - Upload a PDF/DOCX with some dates
   - Click "Extract Dates"

3. Check if events appear in the calendar

## Custom Domain (Optional)

### For Vercel (Frontend):
1. Go to your project settings in Vercel
2. Click "Domains"
3. Add your custom domain
4. Follow DNS configuration instructions

### For Railway (Backend):
1. Go to your project settings in Railway
2. Click "Settings" → "Custom Domain"
3. Add your custom domain
4. Update DNS records as instructed
5. Update `REACT_APP_API_URL` in Vercel to use your custom backend domain

## Environment Variables Summary

### Backend (Railway):
- `PORT` - Auto-set by Railway
- `ANTHROPIC_API_KEY` - (Optional) For AI fallback

### Frontend (Vercel):
- `REACT_APP_API_URL` - Your Railway backend URL (e.g., `https://your-app.railway.app`)

## Updating Your Deployment

### Backend Updates:
```bash
git add backend/
git commit -m "Update backend"
git push
```
Railway will automatically redeploy.

### Frontend Updates:
```bash
git add frontend/
git commit -m "Update frontend"
git push
```
Vercel will automatically redeploy.

## Troubleshooting

### Backend Issues:

**Error: "Module not found"**
- Check that `requirements.txt` includes all dependencies
- Redeploy on Railway

**Error: "Application failed to start"**
- Check Railway logs: Click on your project → "Deployments" → Select latest → "View Logs"
- Ensure `Procfile` exists and contains: `web: gunicorn app:app`

**Error: "Port already in use"**
- Railway handles ports automatically, ensure code uses: `port = int(os.environ.get('PORT', 5000))`

### Frontend Issues:

**Error: "Network Error" or "Cannot connect to backend"**
- Verify `REACT_APP_API_URL` is set correctly in Vercel
- Check Railway backend is running
- Test backend URL directly: `https://your-app.railway.app/api/health`

**Error: "CORS policy error"**
- Backend should allow all origins for `/api/*` routes (already configured)
- If issues persist, check Railway logs

**Error: "Build failed"**
- Check Vercel build logs
- Ensure `package.json` is in the `frontend` directory
- Verify Node.js version compatibility

### Testing Backend Directly:

Test your Railway backend with curl:
```bash
# Health check
curl https://your-app.railway.app/api/health

# Should return: {"status":"ok"}
```

## Cost Estimates

### Free Tier Limits:

**Railway:**
- $5 free credit per month
- Enough for ~500 hours of uptime
- Perfect for low-traffic apps

**Vercel:**
- 100 GB bandwidth per month
- Unlimited personal projects
- Free custom domains

### Scaling Considerations:

If you exceed free tier:
- Railway: ~$0.000463/minute ($20/month for 24/7 uptime)
- Vercel: Generally stays free for personal projects

## Security Notes

1. **API Keys**: Never commit API keys to git
2. **Environment Variables**: Use Railway/Vercel environment variables for secrets
3. **File Uploads**: Current limit is 16MB (configured in `app.py`)
4. **HTTPS**: Both Railway and Vercel provide automatic HTTPS

## Monitoring

### Railway:
- View logs: Project → Deployments → View Logs
- Monitor usage: Project → Settings → Usage

### Vercel:
- View logs: Project → Deployments → [Select Deployment] → Logs
- Monitor analytics: Project → Analytics

## Support

If you encounter issues:
1. Check Railway logs for backend errors
2. Check Vercel logs for frontend errors
3. Verify environment variables are set correctly
4. Test backend health endpoint: `/api/health`

## Next Steps

After deployment:
1. Test with various syllabus formats
2. Share the URL with friends/classmates
3. Collect feedback for improvements
4. Consider adding features like calendar export (iCal, Google Calendar)

Your app is now live and accessible from anywhere in the world!
