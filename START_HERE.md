# 🚀 JUST DO THIS (30 seconds to working app)

## Step 1️⃣ (If you're on Windows):
```
Double-click: quick_test.bat
```

## Step 2️⃣ (If you're on Mac/Linux):
```bash
chmod +x quick_test.sh
./quick_test.sh
```

## Step 3️⃣ (If the above didn't work):
```bash
pip install flask flask-cors python-dotenv
python main.py
```

## Step 4️⃣ (Once you see this):
```
 * Running on http://0.0.0.0:8000
```

## Step 5️⃣ (Open your web browser):
```
http://localhost:8000/health
```

## Step 6️⃣ (You should see):
```json
{
  "status": "healthy",
  "service": "codeplex-ai",
  "version": "1.0.0"
}
```

---

## 🎉 DONE! Your app works!

---

## Want to test more endpoints?

```
# Health check
http://localhost:8000/health

# List AI providers
http://localhost:8000/api/models

# Try analyze (needs API key, but will show error message)
POST http://localhost:8000/api/analyze
Content: {"code": "print('hello')", "provider": "openai"}
```

---

## If it doesn't work:

1. **"Python not found error"** → Install Python from python.org
2. **"pip not found"** → Use `python -m pip` instead
3. **"Port 8000 in use"** → Change port: `set API_PORT=8001` then run
4. **Other errors** → Read `CAN_IT_WORK.md`

---

## That's it! 🚀

Your Codeplex AI app is running!

For more features, read other markdown files in the folder.

