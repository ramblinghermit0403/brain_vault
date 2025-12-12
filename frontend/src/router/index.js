import { createRouter, createWebHistory } from 'vue-router';
import { useAuthStore } from '../stores/auth';

const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes: [
        {
            path: '/',
            name: 'landing',
            component: () => import('../views/LandingPage.vue'),
            meta: { requiresAuth: false }
        },
        {
            path: '/dashboard',
            name: 'dashboard',
            component: () => import('../views/DashboardView.vue'),
            meta: { requiresAuth: true }
        },
        {
            path: '/inbox',
            name: 'inbox',
            component: () => import('../views/InboxView.vue'),
            meta: { requiresAuth: true }
        },
        {
            path: '/login',
            name: 'login',
            component: () => import('../views/LoginView.vue')
        },
        {
            path: '/register',
            name: 'register',
            component: () => import('../views/RegisterView.vue')
        },
        {
            path: '/settings',
            name: 'settings',
            component: () => import('../views/SettingsView.vue'),
            meta: { requiresAuth: true }
        },
        {
            path: '/editor/:id',
            name: 'editor',
            component: () => import('../views/EditorView.vue'),
            meta: { requiresAuth: true }
        },
        {
            path: '/prompts',
            name: 'prompts',
            component: () => import('../views/PromptGeneratorView.vue'),
            meta: { requiresAuth: true }
        },
        {
            path: '/map',
            name: 'map',
            component: () => import('../views/MemoryMapView.vue')
        }
    ]
});

router.beforeEach((to, from, next) => {
    const authStore = useAuthStore();

    // If accessing a protected route and not authenticated, redirect to login
    if (to.meta.requiresAuth && !authStore.isAuthenticated) {
        next('/login');
    }
    // If accessing landing page (root) and already authenticated, redirect to dashboard
    else if (to.path === '/' && authStore.isAuthenticated) {
        next('/dashboard');
    }
    else {
        next();
    }
});

export default router;
