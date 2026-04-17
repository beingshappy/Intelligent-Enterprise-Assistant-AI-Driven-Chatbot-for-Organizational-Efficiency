import subprocess
import time
import sys
import os
import webbrowser

def start_backend():
    print("[SERVER] Starting Backend Server...")
    try:
        if os.name == 'nt': # Windows
            subprocess.Popen(['start', 'cmd', '/k', 'py', 'main.py'], shell=True, cwd='backend')
        else:
            subprocess.Popen(['py', 'main.py'], cwd='backend')
        return True
    except Exception as e:
        print(f"ERROR: Failed to start backend: {e}")
        return False

def start_frontend():
    print("[SERVER] Starting Frontend Server...")
    try:
        if os.name == 'nt':
            subprocess.Popen(['start', 'cmd', '/k', 'py', '-m', 'http.server', '3000'], shell=True, cwd='frontend')
        else:
            subprocess.Popen(['py', '-m', 'http.server', '3000'], cwd='frontend')
        return True
    except Exception as e:
        print(f"ERROR: Failed to start frontend: {e}")
        return False

def main():
    print("="*50)
    print("[LAUNCHER] ENTERPRISE AI - COLLEGE DEMO AUTO-START")
    print("="*50)
    
    if start_backend():
        print("Waiting for AI Engine and Database to initialize (this may take 10-15 seconds)...")
        time.sleep(12) # Increased for stability
        if start_frontend():
            time.sleep(2)
            print("\nOpening Dashboard in your browser...")
            webbrowser.open("http://localhost:3000")
            print("\nSUCCESS: Production Environment is LIVE!")
            print("-" * 50)
            print("[ROLE 1: ADMIN] admin@company.com / admin123")
            print("  - Permissions: AI Assistant, Documents, Analytics Panel")
            print("  - Master OTP: 123456")
            print("-" * 50)
            print("[ROLE 2: EMPLOYEE] employee@company.com / employee123")
            print("  - Permissions: AI Assistant, Document Center (View/Ask)")
            print("  - Tip: You can also use the 'Sign Up' button below.")
            print("-" * 50)
    
    print("="*50)

if __name__ == "__main__":
    main()
