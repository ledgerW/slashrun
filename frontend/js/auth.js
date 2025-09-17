import { validateEmail, validateNonEmpty } from './utils/validation.js';

class AuthManager {
    constructor(storage = window.localStorage) {
        this.storage = storage;
        this.tokenKey = 'slashrun_access_token';
        this.userKey = 'slashrun_user';
    }

    storeAuth(loginResponse) {
        this.storage.setItem(this.tokenKey, loginResponse.access_token);
        const userData = {
            user_id: loginResponse.user_id,
            username: loginResponse.username,
            email: loginResponse.email,
            expires_at: Date.now() + (loginResponse.expires_in * 1000)
        };
        this.storage.setItem(this.userKey, JSON.stringify(userData));
    }

    getUser() {
        const raw = this.storage.getItem(this.userKey);
        if (!raw) return null;
        try {
            return JSON.parse(raw);
        } catch {
            return null;
        }
    }

    getToken() {
        const user = this.getUser();
        if (!user || Date.now() > user.expires_at) {
            this.clearAuth();
            return null;
        }
        return this.storage.getItem(this.tokenKey);
    }

    isAuthenticated() {
        return Boolean(this.getToken());
    }

    clearAuth() {
        this.storage.removeItem(this.tokenKey);
        this.storage.removeItem(this.userKey);
    }

    async login(email, password) {
        if (!validateEmail(email)) {
            return { success: false, error: 'Enter a valid email address.' };
        }
        if (!validateNonEmpty(password)) {
            return { success: false, error: 'Password is required.' };
        }

        const response = await fetch('/api/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });

        if (!response.ok) {
            const error = await response.json().catch(() => ({ detail: 'Login failed' }));
            return { success: false, error: error.detail || 'Login failed' };
        }

        const data = await response.json();
        this.storeAuth(data);
        return { success: true, user: data };
    }

    logout() {
        this.clearAuth();
        window.location.href = '/login.html';
    }

    requireAuth() {
        if (!this.isAuthenticated()) {
            window.location.href = '/login.html';
            return false;
        }
        return true;
    }
}

export const auth = new AuthManager();

const loginForm = document.getElementById('login-form');
if (loginForm) {
    const errorElement = document.getElementById('login-error');
    loginForm.addEventListener('submit', async (event) => {
        event.preventDefault();
        const formData = new FormData(loginForm);
        const email = formData.get('email');
        const password = formData.get('password');
        const result = await auth.login(email, password);
        if (result.success) {
            window.location.href = '/dashboard.html';
        } else if (errorElement) {
            errorElement.textContent = result.error;
        }
    });
}

export function attachAuthGuard() {
    return auth.requireAuth();
}
