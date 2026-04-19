"Mere project folder me 'ULTIMATE_HINGLISH_SETUP.md' file he. Use read karo aur usme diye gaye steps follow karke project ko naye device par setup aur run karo. Make sure Step 6 (Seeding) aur Step 7 (Launch) success ho jayein."

"Failed to fetch error aa raha he. Please backend/main.py ki CORS settings me Port 3000 aur 5500 ko explicitly allow karo, aur frontend/js/auth.js me API_URL ko 'http://127.0.0.1:8000/api' par set karke stabilize karo."




# Intelligent Enterprise Assistant - Setup Instructions

Follow these steps to set up and run the production-ready Enterprise AI Chatbot locally.

## Prerequisite
- Python 3.10+
- MongoDB (Local or Atlas)
- Internet connection (for downloading NLP models on first run)

## 1. Backend Setup
1. Open a terminal in the `backend/` directory.
2. Create a virtual environment:
   ```bash
   py -m venv venv
   .\venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Configure environment:
   - Rename `.env.example` to `.env`.
   - Update `MONGODB_URI` if your MongoDB isn't on `localhost:27017`.
   - (Optional) Add your SMTP credentials if you want real 2FA emails.
5. Start the server:
   ```bash
   py main.py
   ```
   The backend will be live at `http://localhost:8000`.

## 2. Frontend Setup
1. The frontend is built with Vanilla HTML/CSS/JS.
2. You can use any static server to serve the `frontend/` folder.
   - Example using Python:
     ```bash
     cd frontend
     py -m http.server 3000
     ```
3. Open your browser at `http://localhost:3000`.

## 3. Usage Guide
1. **Register**: Click "Register" and create an account.
2. **Login**: Sign in with your email/password.
3. **2FA**: Check your terminal console (or email) for the 6-digit OTP. Enter it to gain access.
4. **Chat**: You can start chatting with the AI immediately.
5. **RAG (Admin)**: 
   - Change your user role to `admin` directly in MongoDB to upload documents.
   - Once uploaded, the bot will use that text to answer your questions.
6. **Bad Language**: Try typing a banned word (e.g., "idiot") to see the filter in action.

## 4. Troubleshooting
- **Model Download**: On the first start, the AI engine will download the `all-MiniLM-L6-v2` model (~80MB). This might take a minute depending on your speed.
- **CORS Error**: Ensure the backend is running at port 8000.
