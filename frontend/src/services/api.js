import axios from 'axios';
import router from '../router';
// Delay store import or use inside interceptor
// import { useAuthStore } from '../stores/auth'; // Removed top-level import

const api = axios.create({
    baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1',
    headers: {
        'Content-Type': 'application/json',
    },
});

// Add a request interceptor to inject the token
api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => Promise.reject(error)
);

let isRefreshing = false;
let failedQueue = [];

const processQueue = (error, token = null) => {
    failedQueue.forEach(prom => {
        if (error) {
            prom.reject(error);
        } else {
            prom.resolve(token);
        }
    });
    failedQueue = [];
};

// Add a response interceptor to handle 401 errors
api.interceptors.response.use(
    (response) => response,
    async (error) => {
        const originalRequest = error.config;

        if (error.response && error.response.status === 401 && !originalRequest._retry) {
            if (isRefreshing) {
                return new Promise(function (resolve, reject) {
                    failedQueue.push({ resolve, reject });
                }).then(token => {
                    originalRequest.headers['Authorization'] = 'Bearer ' + token;
                    return api(originalRequest);
                }).catch(err => {
                    return Promise.reject(err);
                });
            }

            originalRequest._retry = true;
            isRefreshing = true;

            // Dynamic import to avoid circular dependency
            const { useAuthStore } = await import('../stores/auth');
            const authStore = useAuthStore();

            try {
                const newToken = await authStore.refresh();
                isRefreshing = false;
                processQueue(null, newToken);
                originalRequest.headers['Authorization'] = 'Bearer ' + newToken;
                return api(originalRequest);
            } catch (err) {
                isRefreshing = false;
                processQueue(err, null);
                authStore.logout();
                router.push({
                    path: '/login',
                    query: { redirect: router.currentRoute.value.fullPath }
                });
                return Promise.reject(err);
            }
        }
        return Promise.reject(error);
    }
);

export default api;
