import os
import sys
import subprocess
import shutil

def check_python():
    print("[CHECK] Checking Python version...")
    print(f"OK - Found Python: {sys.version}")

def check_libraries():
    print("\n[CHECK] Checking required libraries...")
    libs = [
        "fastapi", "uvicorn", "motor", "transformers", "torch", 
        "sentence_transformers", "pdfplumber", "docx", "redis", "pytesseract", "psutil"
    ]
    missing = []
    for lib in libs:
        try:
            # Special case for binary imports
            name = lib.replace("-", "_")
            if lib == "docx": name = "docx"
            if lib == "pytesseract": name = "pytesseract"
            
            __import__(name)
            print(f"OK - {lib} is installed")
        except ImportError:
            missing.append(lib)
            print(f"MISSING - {lib}")
    return missing

def check_external_deps():
    print("\n[CHECK] Checking External Dependencies...")
    # Check Tesseract OCR
    tesseract = shutil.which("tesseract")
    if tesseract:
        print(f"OK - Tesseract OCR found at: {tesseract}")
    else:
        print("WARN - Tesseract OCR NOT FOUND. OCR features will be disabled.")
    
    # Check MongoDB
    try:
        from pymongo import MongoClient
        uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
        client = MongoClient(uri, serverSelectionTimeoutMS=2000)
        client.server_info()
        print("OK - MongoDB is RUNNING")
    except Exception as e:
        print(f"FAIL - MongoDB is NOT REACHABLE: {e}")

def main():
    print("="*50)
    print("[SYSTEM DIAGNOSTIC] ENTERPRISE AI v2.0")
    print("="*50)
    
    check_python()
    missing = check_libraries()
    check_external_deps()
    
    print("\n" + "="*50)
    if missing:
        print(f"WARN: System is NOT READY. Please run: pip install -r backend/requirements.txt")
    else:
        print("SUCCESS: SYSTEM IS READY FOR THE PRODUCTION DEMO!")
    print("="*50)

if __name__ == "__main__":
    main()
