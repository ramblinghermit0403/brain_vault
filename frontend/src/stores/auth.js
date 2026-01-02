import { defineStore } from 'pinia';
import api from '../services/api';
import { jwtDecode } from "jwt-decode";

export const useAuthStore = defineStore('auth', {
    state: () => {
        const token = localStorage.getItem('token');
        const refreshToken = localStorage.getItem('refreshToken');
        let user = null;

        const decodeUser = (t) => {
            try {
                const decoded = jwtDecode(t);
                return {
                    id: decoded.sub,
                    email: decoded.email || decoded.sub,
                    name: decoded.name || (decoded.email || decoded.sub || '').split('@')[0]
                };
            } catch (e) {
                return null;
            }
        };

        if (token) {
            user = decodeUser(token);
            if (!user) localStorage.removeItem('token');
        }

        return {
            user,
            token: token || null,
            refreshToken: refreshToken || null,
            isAuthenticated: !!token,
        };
    },
    actions: {
        async login(email, password) {
            try {
                const response = await api.post('/auth/login',
                    new URLSearchParams({ username: email, password }),
                    { headers: { 'Content-Type': 'application/x-www-form-urlencoded' } }
                );

                this.setTokens(response.data.access_token, response.data.refresh_token);
                return true;
            } catch (error) {
                console.error('Login failed:', error);
                throw error;
            }
        },

        setTokens(accessToken, refreshToken) {
            this.token = accessToken;
            this.refreshToken = refreshToken; // May be undefined if not provided
            this.isAuthenticated = true;

            localStorage.setItem('token', accessToken);
            if (refreshToken) {
                localStorage.setItem('refreshToken', refreshToken);
            }

            // buffer decode
            try {
                const decoded = jwtDecode(accessToken);
                this.user = {
                    id: decoded.sub,
                    email: decoded.email || decoded.sub,
                    name: decoded.name || (decoded.email || decoded.sub || '').split('@')[0]
                };
            } catch (e) { console.error("Token decode failed", e); }
        },

        async refresh() {
            if (!this.refreshToken) throw new Error("No refresh token");
            try {
                // Bypass interceptor to avoid infinite loop -> Create new instance or use fetch?
                // Actually if we use same api instance, we must flag this request to skip interceptor logic or handle it carefully.
                // Simpler: Use fetch or a naked axios call for refresh to avoid circular dependency in interceptors.
                const response = await fetch('http://localhost:8000/api/v1/auth/refresh', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ refresh_token: this.refreshToken })
                });

                if (!response.ok) throw new Error("Refresh failed");
                const data = await response.json();

                this.setTokens(data.access_token, data.refresh_token || this.refreshToken);
                return data.access_token;
            } catch (e) {
                this.logout();
                throw e;
            }
        },

        async register(email, password, name) {
            try {
                await api.post('/auth/register', { email, password, name });
                return true;
            } catch (error) {
                console.error('Registration failed:', error);
                throw error;
            }
        },
        logout() {
            this.user = null;
            this.token = null;
            this.refreshToken = null;
            this.isAuthenticated = false;
            localStorage.removeItem('token');
            localStorage.removeItem('refreshToken');
        },
    },
});
