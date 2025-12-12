import { defineStore } from 'pinia';
import api from '../services/api';
import { jwtDecode } from "jwt-decode";

export const useAuthStore = defineStore('auth', {
    state: () => {
        const token = localStorage.getItem('token');
        let user = null;
        if (token) {
            try {
                const decoded = jwtDecode(token);
                if (!decoded.email) {
                    throw new Error("Token missing email claim");
                }
                user = {
                    email: decoded.email,
                    name: decoded.name || decoded.email.split('@')[0] // Fallback if name is missing
                };
            } catch (e) {
                localStorage.removeItem('token');
            }
        }
        return {
            user,
            token: token || null,
            isAuthenticated: !!token, // Ensure we check if token is valid? Simplify for now.
        };
    },
    actions: {
        async login(email, password) {
            try {
                const response = await api.post('/auth/login',
                    new URLSearchParams({ username: email, password }),
                    { headers: { 'Content-Type': 'application/x-www-form-urlencoded' } }
                );
                this.token = response.data.access_token;
                this.isAuthenticated = true;
                localStorage.setItem('token', this.token);

                try {
                    const decoded = jwtDecode(this.token);
                    console.log('Decoded Token (Login):', decoded); // Debug log
                    this.user = {
                        email: decoded.email || decoded.sub,
                        name: decoded.name || (decoded.email || decoded.sub).split('@')[0]
                    };
                } catch (e) {
                    console.error("Token decode failed", e);
                }

                return true;
            } catch (error) {
                console.error('Login failed:', error);
                throw error;
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
            this.isAuthenticated = false;
            localStorage.removeItem('token');
        },
    },
});
