# Deploying Django WeatherApp to Vercel

This guide explains how to deploy your Django weather application to Vercel step by step.

---

## Prerequisites

1. **GitHub account** - Vercel deploys from GitHub repositories
2. **Vercel account** - Sign up at https://vercel.com (free tier available)
3. **OpenWeatherMap API key** - Already needed for the app
4. **Your code pushed to GitHub** - Vercel deploys from a git repo

---

## Step 1: Push Your Code to GitHub

If you haven't already pushed your code:

```bash
cd "/home/sifat/Weather App/django_weather_app"

# Initialize git (if not already)
git init

# Add all files
git add -A

# Commit
git commit -m "Initial commit - Django WeatherApp"

# Add your GitHub repo as remote
git remote add origin https://github.com/YOUR_USERNAME/django-weather-app.git

# Push
git branch -M main
git push -u origin main
```

Replace `YOUR_USERNAME` with your actual GitHub username.

---

## Step 2: Sign Up / Log In to Vercel

1. Go to https://vercel.com
2. Click "Sign Up" or "Log In"
3. Authorize Vercel with your GitHub account

---

## Step 3: Import Your Project

1. In Vercel dashboard, click **"Add New"** → **"Project"**
2. Find your repository **"django-weather-app"** and click **"Import"**
3. Configure project settings:

### Project Configuration

**Project Name:** `django-weather-app` (or your preferred name)

**Framework Preset:** Select **"Django"**

If Django preset is not available, use "Other" and configure manually.

---

## Step 4: Configure Environment Variables

In Vercel project settings → **"Environment Variables"**, add these:

### Required Variables

| Key | Value | Description |
|-----|-------|-------------|
| `DJANGO_SECRET_KEY` | [Generate a random string] | Secret key for Django |
| `OPENWEATHER_API_KEY` | your_api_key_here | OpenWeatherMap API key |
| `DEBUG` | `False` | Production mode |
| `DATABASE_URL` | [Auto-filled by Vercel] | PostgreSQL database URL |

### How to Generate DJANGO_SECRET_KEY

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Copy the output and paste as `DJANGO_SECRET_KEY` value.

---

## Step 5: Configure Build Settings

In Vercel project settings → **"General"** → **"Build and Output Settings"**:

### Build Command
```bash
cd django_weather_app && python manage.py migrate
```

### Output Directory
```
django_weather_app
```

### Install Command
```bash
cd django_weather_app && pip install -r requirements.txt
```

---

## Step 6: Enable PostgreSQL Database (Optional but Recommended)

Vercel provides PostgreSQL for free (up to 1 database):

1. In your Vercel project, go to **"Storage"** tab
2. Click **"Create Database"**
3. Select **"PostgreSQL"**
4. Choose **"Free tier"**
5. Click **"Create"**
6. Vercel will automatically create `DATABASE_URL` environment variable

**Note:** If you skip this, the app uses SQLite (not recommended for production on Vercel as file storage is ephemeral).

---

## Step 7: Deploy!

1. Click **"Deploy"** button in Vercel
2. Wait for build to complete (2-5 minutes)
3. Your app will be live at: `https://your-project-name.vercel.app`

---

## Step 8: Post-Deployment Setup

### 1. Create Superuser (Admin Access)

After deployment, you need to create an admin user:

Open Vercel project → **"Functions"** → Find the Django function → Click **"Shell"** (or use Vercel CLI):

```bash
# Run Django management commands
python manage.py migrate --run-syncdb
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

Follow prompts to create username/email/password for admin.

**Alternative:** Use Vercel CLI locally:

```bash
npm i -g vercel
vercel link  # Link to your project
vercel env pull .env.local  # Download environment variables
vercel ssh  # Connect to production shell
# Then run Django commands
```

### 2. Access Admin Panel

Go to: `https://your-app.vercel.app/admin/`

Login with superuser credentials to manage:
- Users
- Cities
- Weather data
- Alerts

---

## Step 9: Test Your Live App

1. Visit your Vercel URL
2. Register a new account
3. Add a city (e.g., "London, GB")
4. Check if weather displays
5. Create an alert
6. Click "Refresh" to test alert triggering

---

## Troubleshooting Vercel Deployment

### Error: "ModuleNotFoundError: No module named 'dotenv'"

**Fix:** Ensure `requirements.txt` includes all dependencies.

```
pip freeze > requirements.txt
```

Then commit and push.

### Error: "ImproperlyConfigured: The SECRET_KEY setting must not be empty."

**Fix:** Set `DJANGO_SECRET_KEY` in Vercel environment variables.

### Error: "OperationalError: no such table: weather_app_city"

**Fix:** Run migrations:
```bash
vercel ssh
cd django_weather_app
python manage.py migrate
```

### Error: "Static files not loading (CSS missing)"

**Fix:** Collect static files:
```bash
vercel ssh
cd django_weather_app
python manage.py collectstatic --noinput
```

### Error: "Error: Cannot find module 'django_weather_app.wsgi'"

**Fix:** Check `vercel.json` configuration. Ensure `WSGI_APPLICATION` in `settings.py` points to `'weather_project.wsgi.application'`.

### Build fails: "Could not find a version that satisfies the requirement"

**Fix:** Update package versions in `requirements.txt`. Use:
```
pip install "package-name" --upgrade
pip freeze > requirements.txt
```

### 500 Internal Server Error

**Fix:** Check Vercel function logs:
1. Go to Vercel project → "Functions"
2. Click on your Django function
3. View "Logs" tab
4. Look for the exact error message

### Database connection issues

**Fix:** Ensure `DATABASE_URL` is set in Vercel environment variables (auto-created when you add PostgreSQL storage).

---

## Important Notes About Vercel + Django

### 1. Serverless Functions Limitations
- Vercel runs Django as a serverless function
- Cold starts: First request may be slower (1-3 seconds)
- Request timeout: 60 seconds for free tier
- Ephemeral filesystem: Files uploaded won't persist (use S3 for user uploads)

### 2. Database
- Use **PostgreSQL** (not SQLite) - Vercel's filesystem is read-only except `/tmp`
- Vercel provides free PostgreSQL via Storage tab
- Connect using `DATABASE_URL` environment variable

### 3. Static & Media Files
- **Static files** (CSS, JS) - Handled by WhiteNoise + collected to `staticfiles/`
- **Media files** (user uploads) - Need external storage (AWS S3, Cloudinary)
- Current app has no user uploads, so static files only

### 4. Environment Variables
- Set in Vercel dashboard (Project → Settings → Environment Variables)
- Never commit `.env` file to git
- Use `.env.example` as template

### 5. Migrations on Every Deploy
Vercel's filesystem resets on each deploy. Add this to your `vercel.json`:

```json
{
  "builds": [...],
  "routes": [...],
  "env": {...},
  "build": {
    "env": {
      "DJANGO_SETTINGS_MODULE": "weather_project.settings"
    }
  }
}
```

Better: Add a **post-deploy hook** via Vercel's "Cron Jobs" or use **Vercel's Serverless PostgreSQL** which persists.

---

## Alternative: Deploy to Railway (Easier for Django)

Vercel is not ideal for Django. Consider **Railway** instead:

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Initialize project
railway init

# Deploy
railway up
```

Railway has better Django support with persistent storage and simpler configuration.

---

## Quick Local Test Before Deploying

```bash
# Test production settings locally
cd django_weather_app

# Set production-mode env variables
export DEBUG=False
export DJANGO_SECRET_KEY=test-secret-key

# Test database connection
python manage.py check --deploy

# Run server
python manage.py runserver
```

Fix any errors before deploying.

---

## Rollback if Something Goes Wrong

In Vercel:
1. Go to your project
2. Click **"Deployments"** tab
3. Find the previous working deployment
4. Click **"Promote to Production"** (three dots menu)

This rolls back instantly.

---

## Summary Checklist

Before pushing to Vercel:

- [ ] Code pushed to GitHub
- [ ] `requirements.txt` includes all packages (`pip freeze > requirements.txt`)
- [ ] `DJANGO_SECRET_KEY` set in Vercel environment
- [ ] `OPENWEATHER_API_KEY` set in Vercel environment
- [ ] `DEBUG=False` in Vercel environment
- [ ] PostgreSQL database added in Vercel Storage
- [ ] `vercel.json` configured
- [ ] Static files configured with WhiteNoise
- [ ] `python manage.py collectstatic` runs without errors
- [ ] `python manage.py check --deploy` passes locally

---

## Files You Should Have for Vercel

```
django_weather_app/
├── vercel.json              ✓ (Vercel config)
├── runtime.txt              ✓ (Python version)
├── requirements.txt         ✓ (Dependencies)
├── .env.example            ✓ (Template)
├── manage.py
├── weather_project/
│   └── settings.py          ✓ (Updated for Vercel)
└── weather_app/
    └── ... (your code)
```

---

## Need Help?

- **Vercel Django Guide:** https://vercel.com/guides/deploying-django
- **Vercel Support:** https://vercel.com/support
- **Django Deployment Checklist:** https://docs.djangoproject.com/en/6.0/howto/deployment/checklist/

---

**Your app is ready!** Follow these steps and your weather app will be live on Vercel within minutes.
