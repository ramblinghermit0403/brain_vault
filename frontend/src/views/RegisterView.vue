<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full space-y-8 bg-white p-10 rounded-xl shadow-sm border border-gray-100">
      <div class="text-center">
        <div class="mx-auto h-12 w-12 bg-blue-100 rounded-full flex items-center justify-center">
          <svg class="h-6 w-6 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" />
          </svg>
        </div>
        <h2 class="mt-6 text-2xl font-bold text-gray-900">
          Create Account
        </h2>
        <p class="mt-2 text-sm text-gray-600">
          Join <span class="font-semibold text-blue-600">Brain Vault</span> today
        </p>
      </div>

      <form class="mt-8 space-y-6" @submit.prevent="handleRegister">
        <div class="space-y-4">
          <div>
            <label for="email-address" class="block text-sm font-medium text-gray-700 mb-1">Email address</label>
            <input id="email-address" name="email" type="email" autocomplete="email" required v-model="email" class="appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm" placeholder="you@example.com" />
          </div>
          
          <div>
            <label for="password" class="block text-sm font-medium text-gray-700 mb-1">Password</label>
            <input id="password" name="password" type="password" autocomplete="new-password" required v-model="password" class="appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm" placeholder="••••••••" />
          </div>
        </div>

        <div>
          <button type="submit" :disabled="loading" class="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-70 disabled:cursor-not-allowed transition-colors duration-200">
            <span class="absolute left-0 inset-y-0 flex items-center pl-3">
              <svg v-if="!loading" class="h-5 w-5 text-blue-200 group-hover:text-blue-100" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" />
              </svg>
              <svg v-else class="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
            </span>
            {{ loading ? 'Creating Account...' : 'Create Account' }}
          </button>
        </div>
        
        <div v-if="error" class="rounded-md bg-red-50 p-4">
          <div class="flex">
            <div class="flex-shrink-0">
              <svg class="h-5 w-5 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div class="ml-3">
              <h3 class="text-sm font-medium text-red-800">
                {{ error }}
              </h3>
            </div>
          </div>
        </div>
      </form>
      
      <div class="text-center mt-4">
        <p class="text-sm text-gray-600">
          Already have an account? 
          <router-link to="/login" class="font-medium text-blue-600 hover:text-blue-500">
            Sign in
          </router-link>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useAuthStore } from '../stores/auth';
import { useRouter } from 'vue-router';
import { useToast } from 'vue-toastification';

const email = ref('');
const password = ref('');
const loading = ref(false);
const error = ref('');
const authStore = useAuthStore();
const router = useRouter();
const toast = useToast();

const handleRegister = async () => {
  loading.value = true;
  error.value = '';
  try {
    await authStore.register(email.value, password.value);
    // Show success message or auto-login? 
    // For now, alert and redirect to login as per original flow, but cleaner.
    // Ideally we'd use a toast notification.
    toast.success('Registration successful! Please login.');
    router.push('/login');
  } catch (err) {
    error.value = 'Registration failed. Please try again.';
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
/* Minimal styles, no custom animations needed for now */
</style>
