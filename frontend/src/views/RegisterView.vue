<template>
  <div class="min-h-screen flex bg-white font-sans">
    <!-- Left Side: Visual/Branding -->
    <!-- Left Side: Visual/Branding -->
    <!-- Left Side: Visual/Branding -->
    <!-- Left Side: Visual/Branding -->
    <div class="hidden lg:flex w-1/2 bg-black relative items-center justify-center">
        <div class="max-w-md w-full px-12">
            <div class="flex items-center gap-4 mb-6">
                <img src="/image.svg" alt="MemWyre" class="h-12 w-12 object-contain invert" />
                <h1 class="text-5xl font-bold text-white tracking-tight">MemWyre</h1>
            </div>
            <p class="text-lg text-gray-400 mb-12">Your Second Brain, Unlocked.</p>
            
            <div class="space-y-6 text-gray-400 font-mono text-sm">
                <div class="flex items-center gap-4">
                    <span class="text-gray-600">→</span>
                    <span>Instant capture</span>
                </div>
                <div class="flex items-center gap-4">
                    <span class="text-gray-600">→</span>
                    <span>Smart retrieval</span>
                </div>
                <div class="flex items-center gap-4">
                    <span class="text-gray-600">→</span>
                    <span>Neural linking</span>
                </div>
            </div>
        </div>
    </div>

    <!-- Right Side: Form -->
    <div class="w-full lg:w-1/2 flex items-center justify-center px-4 sm:px-6 lg:px-8 py-12">
      <div class="max-w-md w-full space-y-8">
        <div class="text-center">
          <div class="lg:hidden mx-auto h-12 w-12 bg-black flex items-center justify-center mb-4">
                <img src="/image.svg" alt="MemWyre" class="h-8 w-8 object-contain invert" />
          </div>
          <h2 class="text-2xl font-bold text-gray-900 tracking-tight">
            Create Account
          </h2>
          <p class="mt-2 text-sm text-gray-600">
            Get started with your free account
          </p>
        </div>

        <form class="mt-8 space-y-6" @submit.prevent="handleRegister">
          <div class="space-y-4">
            <div>
              <label for="name" class="block text-xs uppercase tracking-wide font-semibold text-gray-500 mb-1">Full Name</label>
              <input id="name" name="name" type="text" autocomplete="name" required v-model="name" class="appearance-none block w-full px-3 py-3 border border-gray-300 rounded-none placeholder-gray-400 focus:outline-none focus:ring-1 focus:ring-black focus:border-black sm:text-sm transition-all" placeholder="John Doe" />
            </div>

            <div>
              <label for="email-address" class="block text-xs uppercase tracking-wide font-semibold text-gray-500 mb-1">Email Address</label>
              <input id="email-address" name="email" type="email" autocomplete="email" required v-model="email" class="appearance-none block w-full px-3 py-3 border border-gray-300 rounded-none placeholder-gray-400 focus:outline-none focus:ring-1 focus:ring-black focus:border-black sm:text-sm transition-all" placeholder="you@example.com" />
            </div>
            
            <div>
              <label for="password" class="block text-xs uppercase tracking-wide font-semibold text-gray-500 mb-1">Password</label>
              <input id="password" name="password" type="password" autocomplete="new-password" required v-model="password" class="appearance-none block w-full px-3 py-3 border border-gray-300 rounded-none placeholder-gray-400 focus:outline-none focus:ring-1 focus:ring-black focus:border-black sm:text-sm transition-all" placeholder="••••••••" />
              <div v-if="password.length > 0 && password.length < 8" class="mt-1 text-xs text-red-500">Password must be at least 8 characters.</div>
            </div>
          </div>

          <div>
            <button type="submit" :disabled="loading" class="group relative w-full flex justify-center py-3 px-4 border border-transparent text-sm font-bold text-white bg-black hover:bg-gray-800 focus:outline-none disabled:opacity-70 transition-all duration-200">
              <span class="absolute left-0 inset-y-0 flex items-center pl-3">
                <svg v-if="!loading" class="h-5 w-5 text-gray-500 group-hover:text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
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
          
          <div v-if="error" class="bg-red-50 p-3 border-l-2 border-red-500">
              <p class="text-sm text-red-700">{{ error }}</p>
          </div>
          
           <div class="relative my-6">
              <div class="absolute inset-0 flex items-center">
                <div class="w-full border-t border-gray-200"></div>
              </div>
              <div class="relative flex justify-center text-xs uppercase tracking-wide">
                <span class="px-2 bg-white text-gray-400">Or continue with</span>
              </div>
          </div>

          <div class="grid grid-cols-2 gap-3">
             <button type="button" class="w-full inline-flex justify-center items-center py-2.5 px-4 border border-gray-300 shadow-sm bg-white text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors">
                 <svg class="h-4 w-4 mr-2" viewBox="0 0 24 24" fill="currentColor"><path d="M12.545,10.239v3.821h5.445c-0.712,2.315-2.647,3.972-5.445,3.972c-3.332,0-6.033-2.701-6.033-6.032s2.701-6.032,6.033-6.032c1.498,0,2.866,0.549,3.921,1.453l2.814-2.814C17.503,2.988,15.139,2,12.545,2C7.021,2,2.543,6.477,2.543,12s4.478,10,10.002,10c8.396,0,10.249-7.85,9.426-11.748L12.545,10.239z"/></svg>
                 Google
             </button>
             <button type="button" class="w-full inline-flex justify-center items-center py-2.5 px-4 border border-gray-300 shadow-sm bg-white text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors">
                  <svg class="h-4 w-4 mr-2" fill="currentColor" viewBox="0 0 24 24"><path fill-rule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" clip-rule="evenodd" /></svg>
                  GitHub
             </button>
          </div>
        </form>
        
        <div class="text-center mt-4">
          <p class="text-sm text-gray-500">
            Already have an account? 
            <router-link to="/login" class="font-bold text-black hover:underline">
              Sign in
            </router-link>
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useAuthStore } from '../stores/auth';
import { useRouter } from 'vue-router';
import { useToast } from 'vue-toastification';

const name = ref('');
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
    await authStore.register(email.value, password.value, name.value);
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
