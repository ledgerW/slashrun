import { auth } from './auth.js';

class APIClient {
    constructor(baseURL = '/api') {
        this.baseURL = baseURL;
    }

    getAuthHeaders() {
        const token = auth.getToken();
        const headers = { 'Content-Type': 'application/json' };
        if (token) {
            headers.Authorization = `Bearer ${token}`;
        }
        return headers;
    }

    async request(method, endpoint, data = undefined) {
        const config = {
            method,
            headers: this.getAuthHeaders()
        };

        if (data !== undefined && method !== 'GET') {
            config.body = JSON.stringify(data);
        }

        const response = await fetch(`${this.baseURL}${endpoint}`, config);
        if (response.status === 401) {
            auth.clearAuth();
            window.location.href = '/login.html';
            throw new Error('Authentication required');
        }
        if (!response.ok) {
            const detail = await response.json().catch(() => ({}));
            const error = detail.detail || detail.message || 'Request failed';
            throw new Error(error);
        }
        if (response.status === 204) {
            return null;
        }
        return response.json();
    }

    get(endpoint) {
        return this.request('GET', endpoint);
    }

    post(endpoint, data) {
        return this.request('POST', endpoint, data);
    }

    put(endpoint, data) {
        return this.request('PUT', endpoint, data);
    }

    delete(endpoint) {
        return this.request('DELETE', endpoint);
    }
}

export const api = new APIClient();
