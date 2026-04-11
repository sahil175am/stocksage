# 🪟 StockSage — Windows Setup Guide

## Step 1: Install Python
1. Go to https://python.org/downloads
2. Download Python 3.11 or 3.12
3. **IMPORTANT:** During install, check ✅ "Add Python to PATH"
4. Click Install Now

Verify: Open Command Prompt and type:
```
python --version
```

---

## Step 2: Extract the ZIP
- Right-click `stocksage.zip` → Extract All
- Choose a folder like `C:\Projects\stocksage`
- Open that folder

---

## Step 3: Open Command Prompt in that folder
- In File Explorer, click the address bar
- Type `cmd` and press Enter
- A Command Prompt opens in that folder

---

## Step 4: Create virtual environment
```cmd
python -m venv venv
```

---

## Step 5: Activate virtual environment
```cmd
venv\Scripts\activate
```
You should see `(venv)` at the start of the prompt.

---

## Step 6: Install dependencies
```cmd
pip install -r requirements.txt
```
(This takes 1–2 minutes)

---

## Step 7: Set up environment file
```cmd
copy .env.example .env
notepad .env
```
In Notepad, change at minimum:
```
SECRET_KEY=any-random-string-you-make-up
```
Save and close.

---

## Step 8: Run the app
```cmd
python run.py
```

---

## Step 9: Open in browser
Go to: http://localhost:5000

---

## 🔁 Every time you want to run it again:
```cmd
cd C:\Projects\stocksage
venv\Scripts\activate
python run.py
```

---

## ❓ Troubleshooting

**"python is not recognized"**
→ Reinstall Python and check "Add to PATH"

**"pip is not recognized"**
→ Run: `python -m pip install -r requirements.txt`

**Port already in use**
→ Run: `python run.py` uses port 5000. Close other apps using it, or edit `run.py` and change `port=5000` to `port=5001`

**venv\Scripts\activate gives an error about execution policy**
→ Run this first, then try again:
```cmd
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```
(only needed if you use PowerShell instead of cmd)
