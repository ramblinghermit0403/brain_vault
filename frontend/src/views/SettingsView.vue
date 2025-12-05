<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900 transition-colors duration-300">
    <nav class="bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between h-16">
          <div class="flex">
            <div class="flex-shrink-0 flex items-center">
              <h1 class="text-xl font-bold text-blue-600">Brain Vault</h1>
            </div>
            <div class="hidden sm:ml-6 sm:flex sm:space-x-8">
              <router-link to="/" class="border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium">
                Dashboard
              </router-link>
              <a href="#" class="border-blue-600 text-gray-900 dark:text-white inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium">
                Settings & Export
              </a>
            </div>
          </div>
          <div class="flex items-center space-x-4">
            <ThemeToggle />
            <button @click="logout" class="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 px-3 py-2 rounded-md text-sm font-medium">
              Logout
            </button>
          </div>
        </div>
      </div>
    </nav>

    <div class="py-10">
      <header>
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h1 class="text-3xl font-bold leading-tight text-gray-900 dark:text-white">
            Settings & Export
          </h1>
        </div>
      </header>
      <main>
        <div class="max-w-7xl mx-auto sm:px-6 lg:px-8">
          <div class="px-4 py-8 sm:px-0 space-y-6">
            
            <!-- API Keys Section -->
            <div class="bg-white dark:bg-gray-800 shadow-sm sm:rounded-lg p-6 border border-gray-100 dark:border-gray-700 transition-colors duration-300">
              <h3 class="text-lg leading-6 font-medium text-gray-900 dark:text-white">API Keys</h3>
              <div class="mt-2 max-w-xl text-sm text-gray-500 dark:text-gray-400">
                <p>Manage your API keys for LLM providers.</p>
              </div>
              <div class="mt-5 space-y-4">
                <div>
                  <label for="openai_key" class="block text-sm font-medium text-gray-700 dark:text-gray-300">OpenAI API Key</label>
                  <input type="password" id="openai_key" v-model="openaiKey" class="mt-1 block w-full border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-white" placeholder="sk-..." />
                </div>
                <div>
                  <label for="gemini_key" class="block text-sm font-medium text-gray-700 dark:text-gray-300">Gemini API Key</label>
                  <input type="password" id="gemini_key" v-model="geminiKey" class="mt-1 block w-full border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-white" placeholder="AIza..." />
                </div>
                <button @click="saveKeys" class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors duration-200">
                  Save Keys
                </button>
              </div>
            </div>

            <!-- Extension Auth Section -->
            <div class="bg-white dark:bg-gray-800 shadow-sm sm:rounded-lg p-6 border border-gray-100 dark:border-gray-700 transition-colors duration-300">
              <h3 class="text-lg leading-6 font-medium text-gray-900 dark:text-white">Browser Extension Auth</h3>
              <div class="mt-2 max-w-xl text-sm text-gray-500 dark:text-gray-400">
                <p>Use this token to log in to the Brain Vault Browser Extension.</p>
              </div>
              <div class="mt-5 flex space-x-4">
                <button @click="copyToken" class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 transition-colors duration-200">
                  <span v-if="tokenCopied">Copied!</span>
                  <span v-else>Copy Extension Token</span>
                </button>
                <button @click="restartTour" class="inline-flex items-center px-4 py-2 border border-gray-300 dark:border-gray-600 shadow-sm text-sm font-medium rounded-md text-gray-700 dark:text-gray-200 bg-white dark:bg-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors duration-200">
                  Restart Tour
                </button>
              </div>
            </div>

            <!-- Export Section -->
            <div class="bg-white dark:bg-gray-800 shadow-sm sm:rounded-lg p-6 border border-gray-100 dark:border-gray-700 transition-colors duration-300">
              <h3 class="text-lg leading-6 font-medium text-gray-900 dark:text-white">Export Data</h3>
              <div class="mt-2 max-w-xl text-sm text-gray-500 dark:text-gray-400">
                <p>Download your entire knowledge base.</p>
              </div>
              <div class="mt-5 flex space-x-4">
                <button @click="exportData('json')" class="inline-flex items-center px-4 py-2 border border-gray-300 dark:border-gray-600 shadow-sm text-sm font-medium rounded-md text-gray-700 dark:text-gray-200 bg-white dark:bg-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors duration-200">
                  Export JSON
                </button>
                <button @click="exportData('md')" class="inline-flex items-center px-4 py-2 border border-gray-300 dark:border-gray-600 shadow-sm text-sm font-medium rounded-md text-gray-700 dark:text-gray-200 bg-white dark:bg-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors duration-200">
                  Export Markdown
                </button>
              </div>
            </div>

          </div>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useAuthStore } from '../stores/auth';
import { useRouter } from 'vue-router';
import api from '../services/api';
import ThemeToggle from '../components/ThemeToggle.vue';
import { useToast } from 'vue-toastification';

const authStore = useAuthStore();
const router = useRouter();
const toast = useToast();
const openaiKey = ref(localStorage.getItem('openai_key') || '');
const geminiKey = ref(localStorage.getItem('gemini_key') || '');
const tokenCopied = ref(false);

const logout = () => {
  authStore.logout();
  router.push('/login');
};

const copyToken = async () => {
  const token = localStorage.getItem('token');
  if (token) {
    try {
      await navigator.clipboard.writeText(token);
      tokenCopied.value = true;
      setTimeout(() => tokenCopied.value = false, 2000);
      toast.success('Token copied to clipboard');
    } catch (err) {
      console.error('Failed to copy token:', err);
      toast.error('Failed to copy token');
    }
  } else {
    toast.error('No token found. Please log in again.');
  }
};

const restartTour = () => {
  localStorage.removeItem('tour_completed');
  router.push('/');
};

const saveKeys = () => {
  localStorage.setItem('openai_key', openaiKey.value);
  localStorage.setItem('gemini_key', geminiKey.value);
  toast.success('Keys saved locally (for MVP).');
};

const exportData = async (format) => {
  try {
    const response = await api.get(`/export/${format}`, { responseType: 'blob' });
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `brain_vault_export.${format}`);
    document.body.appendChild(link);
    link.click();
    toast.success(`Exported as ${format.toUpperCase()}`);
  } catch (error) {
    toast.error('Export failed');
  }
};
</script>
