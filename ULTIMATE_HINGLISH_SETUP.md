# 🚀 Project Setup Guide: Step-by-Step (Hinglish)

Ye guide aapko help karegi is project ko kisi bhi naye device par 10-15 minute me setup karne me. 

---

## 🛠️ Step 1: Jaruri Softwares (Direct Links)

Sabse pehle ye 2 main software install karein:

1.  **Python 3.10.11** (Recommended Version)
    *   **Direct Link**: [Download Python 3.10.11 (Windows 64-bit)](https://www.python.org/ftp/python/3.10.11/python-3.10.11-amd64.exe)
    *   **Note**: Install karte waqt **"Add Python to PATH"** par click zaroor karein.
2.  **MongoDB Community Server** (Database)
    *   **Direct Link**: [Download MongoDB MSI](https://www.mongodb.com/try/download/community)
    *   **Dashboard (Optional)**: [Download MongoDB Compass](https://www.mongodb.com/try/download/compass) (Data dekhne ke liye).

---

## 📂 Step 2: Project Files ko Setup Karein

1.  Project folder ko apne PC me kahi bhi copy karein (Example: `D:/MyProject/`).
2.  Folder ke andar ja kar Terminal (PowerShell/CMD) open karein.

---

## 🐍 Step 3: Python Virtual Environment (Venv)

Isse aapke computer ke baki programs kharab nahi hote aur project stable rehta he.

```powershell
# 1. Virtual environment create karein
py -m venv venv

# 2. Use activate karein
.\venv\Scripts\activate
```

---

## 📦 Step 4: Sari Dependencies Install Karein

Backend ki libraries (FastAPI, AI Models, etc.) install karne ke liye ye command run karein:

```powershell
# Backend folder ke andar requirements.txt se install karein
pip install -r backend/requirements.txt
```

---

## 🔑 Step 5: Environment Variables (`.env`)

Backend folder ke andar ek file banayein jiska naam ho `.env` aur usme ye text paste karein:

```env
MONGODB_URI=mongodb://localhost:27017
DATABASE_NAME=enterprise_assistant
JWT_SECRET=ye-kuch-bhi-secret-dal-do
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

---

## 📂 Step 6: AI Models aur Demo Data Setup (MANDATORY)

> [!CAUTION]
> **IMPORTANT**: Naye device par database khali hota he. Agar aap ye step miss karenge toh login par "Invalid email or password" error aayega.

```powershell
# Database me demo accounts banane ke liye ye run karein:
py seed_demo_data.py
```

Isse aapka **Admin** (`admin@company.com` / `admin123`) aur **Employee** (`employee@company.com` / `employee123`) accounts ready ho jayenge.

---

## 🚀 Step 7: Project Launch (Final Step)

Sab kuch ready he! Ab bus ye launcher command run karein:

```powershell
# Isse backend aur frontend dono ek saath start ho jayenge
py run_demo.py
```

System automatically browser me **http://localhost:3000** open kar dega.

---

## ⚠️ Troubleshooting (Common Problems)

### 1. "Failed to fetch" error
*   **Fix 1**: Ensure karein ki aapne backend server chala rakha he.
*   **Fix 2**: Browser me **Ctrl + F5** dabaiye (Hard Refresh). Maine `auth.js` ko stable kar diya he, toh ye issue ab nahi aayega.

### 2. "Invalid email or password" 
*   **Fix**: Yani aapne Step 6 (`py seed_demo_data.py`) run nahi kiya he. Ise run karein aur default passwords use karein.

### 3. Database Connection Error
*   **Fix**: Ensure kijiye ki MongoDB Service background me "Running" state me he (Task Manager -> Services me check karein).

---

Ab aapka project kisi bhi dusre device par move karne ke liye ready he! 🚀🎓✅
