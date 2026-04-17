const API_URL = 'http://localhost:8000/api';

class AuthService {
    constructor() {
        this.token = localStorage.getItem('token');
        this.user = JSON.parse(localStorage.getItem('user'));
        this.emailPending = null;
    }

    async fetchWithAuth(endpoint, options = {}) {
        const url = `${API_URL}${endpoint}`;
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${this.token}`
            }
        };
        const finalOptions = { ...defaultOptions, ...options };
        
        const response = await fetch(url, finalOptions);
        if (response.status === 401 || response.status === 403) {
            this.logout();
            throw new Error("Session expired or unauthorized");
        }
        return await response.json();
    }

    async register(name, email, password) {
        const response = await fetch(`${API_URL}/auth/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, email, password })
        });
        const data = await response.json();
        if (!response.ok) throw new Error(data.detail || 'Registration failed');
        return data;
    }

    async login(email, password) {
        const response = await fetch(`${API_URL}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });
        const data = await response.json();
        if (!response.ok) throw new Error(data.detail || 'Login failed');
        this.emailPending = email;
        return data;
    }

    async verifyOTP(otp) {
        const response = await fetch(`${API_URL}/auth/verify-otp`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email: this.emailPending, otp })
        });
        const data = await response.json();
        if (!response.ok) throw new Error(data.detail || 'Verification failed');
        
        this.token = data.access_token;
        this.user = { email: this.emailPending, role: data.role };
        localStorage.setItem('token', this.token);
        localStorage.setItem('user', JSON.stringify(this.user));
        return data;
    }

    logout() {
        this.token = null;
        this.user = null;
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        window.location.reload();
    }
}

const auth = new AuthService();
