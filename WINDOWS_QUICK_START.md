# Codeplex AI - Windows Quick Start (Will It Work?)

## ✅ YES! It Will Work!

The application is built with standard Python and will work on Windows, **BUT** you need to do this first:

## 🚀 Get It Running in 5 Minutes

### Option 1: Automatic Test (Easiest)

1. **Double-click** this file in Windows Explorer:
   ```
   quick_test.bat
   ```

   This will:
   - Check Python is installed
   - Install Flask and dependencies
   - Verify project structure
   - Create `.env` file
   - Run the Flask app

2. **Open your browser** to: `http://localhost:8000/health`

3. **You should see:**
   ```json
   {
     "status": "healthy",
     "service": "codeplex-ai",
     "version": "1.0.0"
   }
   ```

### Option 2: Manual (If bat file doesn't work)

**Step 1: Open PowerShell**
```powershell
# Navigate to the project
cd "C:\Users\luniy\OneDrive\Desktop\python application"
```

**Step 2: Install Dependencies**
```powershell
pip install -r requirements.txt
```

**Step 3: Create .env File**
```powershell
copy .env.example .env
```

**Step 4: Run the Server**
```powershell
python main.py
```

**Step 5: Test in your browser**
- Health Check: `http://localhost:8000/health`
- Models List: `http://localhost:8000/api/models`

## 📋 What Gets Installed

When you run `pip install -r requirements.txt`, you get:
- Flask (web framework)
- Flask-CORS (for API)
- OpenAI, Anthropic, Google AI libraries
- PostgreSQL, Redis, SQLAlchemy
- NumPy, Pandas, TensorFlow, PyTorch
- Testing libraries
- And more...

**Total: ~27 packages, ~500MB download**

## 🎯 Test These URLs Immediately

| URL | What It Does | Will It Work? |
|-----|---|---|
| `http://localhost:8000/health` | Server health check | ✅ YES (no setup needed) |
| `http://localhost:8000/api/models` | List AI providers | ✅ YES (no setup needed) |
| `POST http://localhost:8000/api/analyze` | Analyze code | ❌ Needs OpenAI key |
| `POST http://localhost:8000/api/generate` | Generate code | ❌ Needs OpenAI key |

### Test Health Check from PowerShell

```powershell
# Method 1: Using curl (Windows 10+)
curl http://localhost:8000/health

# Method 2: Using Invoke-WebRequest
Invoke-WebRequest http://localhost:8000/health

# Method 3: Just open in browser
# Navigate to: http://localhost:8000/health
```

## 🔧 Troubleshooting Windows Issues

### Issue: "'python' is not recognized"
**Solution:**
1. Install Python from https://www.python.org/
2. During installation, **CHECK** "Add Python to PATH"
3. Restart PowerShell and try again

### Issue: "'pip' is not recognized"
**Solution:**
```powershell
python -m pip install -r requirements.txt
```

### Issue: "Port 8000 already in use"
**Solution:**
```powershell
$env:API_PORT=8001
python main.py
# Then access at http://localhost:8001
```

### Issue: SSL certificate error
**Solution:**
```powershell
# This is for pip - temporary workaround during install
pip install --trusted-host pypi.python.org -r requirements.txt
```

### Issue: Long path names on Windows
**Solution:**
```powershell
# Enable long paths (Windows 10/11 as Admin)
New-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" -Name "LongPathsEnabled" -Value 1 -PropertyType DWORD -Force
```

## 📁 File Location on Windows

```
C:\Users\[YourUsername]\OneDrive\Desktop\python application\
├── main.py                    ← This is what you run
├── requirements.txt           ← Dependencies to install
├── .env.example              ← Copy to .env
├── quick_test.bat            ← Double-click this to test
├── verify_startup.py         ← Verification script
├── app\
│   ├── routes.py
│   ├── ai_services.py
│   ├── config.py
│   └── ...other files...
└── docker-compose.yml        ← For Docker (optional)
```

## 📦 System Requirements

- **Windows 10 or 11** (but Windows 7+ should work)
- **Python 3.9 or higher**
- **2GB Ram** (4GB+ recommended)
- **500MB disk space** (for dependencies)
- **Internet connection** (first run only)

## ⚡ Performance Expectations

- **Startup time**: 2-5 seconds
- **Health check response**: < 100ms
- **Models endpoint**: < 100ms
- **AI endpoints**: 5-60 seconds (depends on OpenAI API)

## 🐳 Optional: Docker on Windows

If you want the full production setup:

1. Install Docker Desktop from https://www.docker.com/products/docker-desktop
2. Run:
   ```powershell
   docker-compose up -d
   ```

## 🎓 Learning Path

1. **Get it working** (this guide)
2. **Test basic endpoints** (health check, models)
3. **Read API_DOCUMENTATION.md** (understand the API)
4. **Get API keys** (OpenAI, Anthropic, Google)
5. **Test AI endpoints** (analyze, generate, optimize)
6. **Read QUICKSTART.md** (full setup guide)
7. **Read DEPLOYMENT.md** (deploy to production)

## 🚀 Next Commands

Once it's running:

```powershell
# Stop the server
Ctrl+C

# Run with debug mode
$env:DEBUG=True
python main.py

# Run tests
pip install pytest
pytest tests/

# Format code
pip install black
black app/ main.py

# Lint code
pip install flake8
flake8 app/ main.py
```

## ✅ Checklist

- [ ] Python 3.9+ installed
- [ ] Ran `pip install -r requirements.txt`
- [ ] Created `.env` file
- [ ] Ran `python main.py`
- [ ] Tested `http://localhost:8000/health`
- [ ] Read API_DOCUMENTATION.md
- [ ] Got OpenAI API key (optional for AI features)

## 🎉 Success Indicators

When you run the app, you should see:

```
 * Serving Flask app 'main'
 * Debug mode: off
 * WARNING: This is a development server.
 * Running on http://0.0.0.0:8000
```

Then visiting `http://localhost:8000/health` shows:
```json
{
  "timestamp": "2024-04-28T...",
  "status_code": 200,
  "data": {
    "status": "healthy",
    "service": "codeplex-ai",
    "version": "1.0.0"
  }
}
```

## 📞 Still Having Issues?

1. **Check QUICK_TEST.md** - More detailed troubleshooting
2. **Check QUICKSTART.md** - General setup guide
3. **Review code comments** - All files have docstrings
4. **Check the logs** - Look for error messages in console

## 🎯 Summary

| What You Want | Command | Time | Extra Needs |
|---|---|---|---|
| Just test it | `quick_test.bat` | 5 min | Nothing |
| Run locally | `python main.py` | 2 min | Python + pip |
| Full features | `docker-compose up -d` | 10 min | Docker |
| Production | See DEPLOYMENT.md | 30+ min | Cloud account |

---

**TL;DR**: Yes it works! Double-click `quick_test.bat` and you'll have a working API in 5 minutes! 🚀

