# Intelligent Enterprise Assistant: AI-Driven Chatbot for Organizational Efficiency (API)

This document provides a professional REST API specification for the platform, including request/response examples and authentication requirements.

---

## 🔸 Authentication Endpoints

### 1. Register Account
`POST /api/auth/register`

**Request Body:**
```json
{
  "name": "Jane Doe",
  "email": "jane@company.com",
  "password": "securepassword123",
  "role": "employee"
}
```

---

### 2. Login (Triggers OTP)
`POST /api/auth/login`

**Request Body:**
```json
{
  "email": "jane@company.com",
  "password": "securepassword123"
}
```
**Success Response:** `{"message": "OTP sent to your email / terminal"}`

---

### 3. Verify OTP & Obtain Token
`POST /api/auth/verify-otp`

**Request Body:**
```json
{
  "email": "jane@company.com",
  "otp": "123456"
}
```
**Success Response:** 
```json
{
  "access_token": "eyJ0eX...",
  "token_type": "bearer",
  "role": "employee"
}
```

---

## 🔸 AI Chat Endpoints

### 4. Direct AI Conversation (RAG Supported)
`POST /api/chat/`
**Header:** `Authorization: Bearer <TOKEN>`

**Request Body:**
```json
{
  "message": "What is the company policy on remote work?",
  "session_id": "optional-id"
}
```
**Response:**
```json
{
  "response": "Based on the internal company records, employees are allowedb = Database()

# Smart Properties for cleaner code and demo stability
@property
def chats(self): return self.db.chats
@property
def users(self): return self.db.users
@property
def documents(self): return self.db.documents

# Bind properties to the instance for 'db.chats' logic
Database.chats = chats
Database.users = users
Database.documents = documents

async def get_database():
 work per week...",
  "context_used": true,
  "timestamp": "2024-04-17T..."
}
```

---

## 🔸 Document Management

### 5. Upload Knowledge Source
`POST /api/documents/`
**Header:** `Authorization: Bearer <TOKEN>`
**Format:** `multipart/form-data`

---

## 🔸 Administrative Panel (Tier 1 Access Only)

### 6. System Analytics
`GET /api/admin/analytics`
**Header:** `Authorization: Bearer <ADMIN_TOKEN>`

**Response:**
```json
{
  "total_chats": 450,
  "system_health": {
    "cpu_usage": 15.4,
    "memory_usage": 42.1
  }
}
```

### 7. Global Audit Logs
`GET /api/admin/logs`
**Header:** `Authorization: Bearer <ADMIN_TOKEN>`
**Purpose:** View real-time query activity across all organizational departments.

---

## 🔸 Enterprise Protection

### Rate Limiting (429)
The system implements a **Leaky Bucket** rate limiter. 
- **Chat Endpoints**: 20 requests/minute.
- **Auth Endpoints**: 5 attempts/minute.
Excessive requests will return: `{"detail": "Too many requests..."}`
