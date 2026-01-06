<template>
  <div class="h-screen flex flex-col bg-gray-50 dark:bg-app transition-colors duration-300 font-sans overflow-hidden">
    <NavBar />
    
    <main class="flex-1 overflow-hidden w-full max-w-4xl mx-auto py-10 px-4 sm:px-6 lg:px-8 flex flex-col h-full">
      <div class="flex-none">
          <div class="mb-8">
            <h1 class="text-3xl font-bold text-gray-900 dark:text-text-primary">Settings</h1>
          </div>

          <!-- Tab Header -->
          <div class="border-b border-gray-200 dark:border-border mb-8 overflow-x-auto [&::-webkit-scrollbar]:hidden [-ms-overflow-style:'none'] [scrollbar-width:'none']">
              <nav class="-mb-px flex space-x-8">
                  <button 
                    @click="activeTab = 'general'"
                    :class="activeTab === 'general' ? 'border-black dark:border-white text-black dark:text-white' : 'border-transparent text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200'"
                    class="whitespace-nowrap pb-4 px-1 border-b-2 font-medium text-sm transition-colors"
                  >
                      General
                  </button>
                  <button 
                    @click="activeTab = 'integration'"
                    :class="activeTab === 'integration' ? 'border-black dark:border-white text-black dark:text-white' : 'border-transparent text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200'"
                    class="whitespace-nowrap pb-4 px-1 border-b-2 font-medium text-sm transition-colors"
                  >
                      Integrations
                  </button>
                  <button 
                    @click="activeTab = 'data'"
                    :class="activeTab === 'data' ? 'border-black dark:border-white text-black dark:text-white' : 'border-transparent text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200'"
                    class="whitespace-nowrap pb-4 px-1 border-b-2 font-medium text-sm transition-colors"
                  >
                      Data & Export
                  </button>
              </nav>
          </div>
      </div>

      <!-- Scrollable Content Area -->
      <div class="flex-1 overflow-y-auto min-h-0 pr-2 custom-scrollbar">
          <!-- General Tab -->
          <div v-show="activeTab === 'general'" class="bg-white dark:bg-surface shadow rounded-lg px-8 py-8 border border-gray-100 dark:border-border animate-fade-in relative">
               
               <h3 class="text-lg leading-6 font-medium text-gray-900 dark:text-white mb-6">Appearance</h3>
               <div class="space-y-6 mb-8">
                   <div class="flex items-center justify-between">
                      <div>
                        <span class="text-sm font-medium text-gray-900 dark:text-white">Theme</span>
                        <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">Customize the look and feel of your workspace.</p>
                      </div>
                      <ThemeToggle />
                   </div>
               </div>
               
               <hr class="border-gray-100 dark:border-border mb-8" />

               <h3 class="text-lg leading-6 font-medium text-gray-900 dark:text-white mb-6">Preferences</h3>
               <div class="space-y-6">
                    <!-- Auto-Approve Toggle -->
                    <div class="flex items-center justify-between">
                       <div>
                        <span class="text-sm font-medium text-gray-900 dark:text-white">Auto-Approve New Memories</span>
                        <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">Automatically add created memories to the vector store without manual review.</p>
                      </div>
                      <button 
                        @click="toggleAutoApprove" 
                        :class="settings.auto_approve ? 'bg-black dark:bg-white' : 'bg-gray-200 dark:bg-gray-700'" 
                        class="relative inline-flex flex-shrink-0 h-6 w-11 border-2 border-transparent rounded-full cursor-pointer transition-colors ease-in-out duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-black dark:focus:ring-white"
                      >
                        <span 
                          aria-hidden="true" 
                          :class="settings.auto_approve ? 'translate-x-5' : 'translate-x-0'" 
                          class="pointer-events-none inline-block h-5 w-5 rounded-full bg-white shadow transform ring-0 transition ease-in-out duration-200"
                        ></span>
                      </button>
                    </div>
                    
                    <hr class="border-gray-100 dark:border-border" />
                    
                    <!-- Account Info (Static for now as mostly mockup) -->
                    <div>
                       <h4 class="text-sm font-medium text-gray-900 dark:text-text-primary mb-4">Account</h4>
                       <div class="grid grid-cols-1 gap-y-6 gap-x-4 sm:grid-cols-6">
                           <div class="sm:col-span-4">
                               <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">Email address</label>
                               <div class="mt-1">
                                   <input type="email" disabled :value="authStore.user?.email || 'user@example.com'" class="bg-gray-50 dark:bg-gray-700 block w-full sm:text-sm border-gray-300 dark:border-gray-600 rounded-md py-2 px-3 text-gray-500 dark:text-gray-400 cursor-not-allowed">
                               </div>
                           </div>
                       </div>
                    </div>
               </div>
          </div>

          <!-- Integrations Tab -->
          <div v-show="activeTab === 'integration'" class="bg-white dark:bg-surface shadow rounded-lg px-8 py-8 border border-gray-100 dark:border-border animate-fade-in">
               <h3 class="text-lg leading-6 font-medium text-gray-900 dark:text-text-primary mb-2">Connected LLM Clients</h3>
               <p class="text-sm text-gray-500 dark:text-text-secondary mb-6">Manage external LLM providers and their permissions.</p>
               
               <!-- Keys List -->
               <div class="space-y-3 mb-8" v-if="keys.length > 0">
                    <div v-for="key in keys" :key="key.id" class="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg border border-gray-200 dark:border-gray-600">
                      <div class="flex items-center gap-3">
                        <div class="p-2 bg-white dark:bg-gray-600 rounded-md shadow-sm">
                            <svg class="w-5 h-5 text-gray-500 dark:text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z" /></svg>
                        </div>
                        <div class="flex flex-col">
                            <span class="font-medium text-gray-900 dark:text-text-primary capitalize">{{ key.provider }}</span>
                            <div class="flex gap-2 mt-0.5">
                                <span v-if="key.permissions.read" class="text-[10px] uppercase font-bold tracking-wider text-black dark:text-white">Read</span>
                                <span v-if="key.permissions.write" class="text-[10px] uppercase font-bold tracking-wider text-black dark:text-white">Write</span>
                            </div>
                        </div>
                      </div>
                      <button @click="deleteKey(key.id)" class="text-gray-400 hover:text-red-600 dark:text-gray-500 dark:hover:text-red-400 p-2 transition-colors">
                          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" /></svg>
                      </button>
                    </div>
               </div>
               
               <!-- Add New Key -->
               <div class="border-t border-gray-100 dark:border-border pt-6">
                    <h4 class="text-sm font-medium text-gray-900 dark:text-text-primary mb-4">Add New Connection</h4>
                    <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 mb-4">
                      <div>
                        <label class="block text-xs font-medium text-gray-500 uppercase tracking-wider mb-1">Provider</label>
                        <div class="relative">
                            <select v-model="newKey.provider" class="block w-full pl-3 pr-10 py-2 text-base border-gray-300 dark:border-gray-600 focus:outline-none focus:ring-black dark:focus:ring-white focus:border-black dark:focus:border-white sm:text-sm rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white appearance-none">
                              <option value="openai">OpenAI</option>
                              <option value="anthropic">Anthropic</option>
                              <option value="gemini">Google Gemini</option>
                            </select>
                            <div class="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-gray-700 dark:text-gray-400">
                                 <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" /></svg>
                            </div>
                        </div>
                      </div>
                      <div>
                        <label class="block text-xs font-medium text-gray-500 uppercase tracking-wider mb-1">API Key</label>
                        <input type="password" v-model="newKey.api_key" class="block w-full border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:ring-black dark:focus:ring-white focus:border-black dark:focus:border-white sm:text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-white py-2 px-3" placeholder="sk-..." />
                      </div>
                    </div>
                    
                    <div class="flex items-center gap-6 mb-6">
                       <label class="inline-flex items-center cursor-pointer">
                        <input type="checkbox" v-model="newKey.permissions.read" class="rounded border-gray-300 text-black shadow-sm focus:border-black focus:ring focus:ring-black focus:ring-opacity-50 dark:bg-gray-700 dark:border-gray-600">
                        <span class="ml-2 text-sm text-gray-600 dark:text-gray-300">Allow Read</span>
                      </label>
                      <label class="inline-flex items-center cursor-pointer">
                        <input type="checkbox" v-model="newKey.permissions.write" class="rounded border-gray-300 text-black shadow-sm focus:border-black focus:ring focus:ring-black focus:ring-opacity-50 dark:bg-gray-700 dark:border-gray-600">
                        <span class="ml-2 text-sm text-gray-600 dark:text-gray-300">Allow Write</span>
                      </label>
                    </div>
                    
                    <button @click="addKey" class="w-full sm:w-auto inline-flex items-center justify-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-black dark:bg-white dark:text-black hover:bg-gray-900 dark:hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-black dark:focus:ring-white transition-colors">
                        Connect Provider
                    </button>
               </div>
               
               <div class="mt-10 pt-8 border-t border-gray-100 dark:border-border">
                  <h3 class="text-lg leading-6 font-medium text-gray-900 dark:text-text-primary mb-2">Browser Extension Auth</h3>
                  <p class="text-sm text-gray-500 dark:text-text-secondary mb-6">Use this token to log in to the Brain Vault extension.</p>
                  
                  <div class="flex items-center gap-4">
                     <button @click="copyToken" class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white dark:text-black bg-black dark:bg-white hover:bg-gray-900 dark:hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-black dark:focus:ring-white transition-colors">
                       <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 5H6a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2v-1M8 5a2 2 0 002 2h2a2 2 0 002-2M8 5a2 2 0 012-2h2a2 2 0 012 2m0 0h2a2 2 0 012 2v3m2 4H10m0 0l3-3m-3 3l3 3" /></svg>
                       <span v-if="tokenCopied">Copied!</span>
                       <span v-else>Copy Token</span>
                     </button>
                     <button @click="restartTour" class="inline-flex items-center px-4 py-2 border border-gray-300 dark:border-gray-600 shadow-sm text-sm font-medium rounded-md text-gray-700 dark:text-gray-200 bg-white dark:bg-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600 transition-colors">
                       Restart Tour
                     </button>
                  </div>
               </div>
          </div>

          <!-- Data Tab -->
          <div v-show="activeTab === 'data'" class="bg-white dark:bg-surface shadow rounded-lg px-8 py-8 border border-gray-100 dark:border-border animate-fade-in">
              <h3 class="text-lg leading-6 font-medium text-gray-900 dark:text-text-primary mb-2">Export Data</h3>
              <p class="text-sm text-gray-500 dark:text-text-secondary mb-6">Download your entire knowledge base in your preferred format.</p>
              
              <div class="flex space-x-4">
                <button @click="exportData('json')" class="inline-flex items-center px-4 py-3 border border-gray-300 dark:border-gray-600 shadow-sm text-sm font-medium rounded-lg text-gray-700 dark:text-gray-200 bg-white dark:bg-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600 transition-colors group">
                  <svg class="w-8 h-8 mr-3 text-gray-400 group-hover:text-black dark:group-hover:text-white transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" /></svg>
                  <div class="text-left">
                      <div class="text-xs text-gray-500 uppercase font-semibold">Format</div>
                      <div class="text-base font-bold">JSON</div>
                  </div>
                </button>
                <button @click="exportData('md')" class="inline-flex items-center px-4 py-3 border border-gray-300 dark:border-gray-600 shadow-sm text-sm font-medium rounded-lg text-gray-700 dark:text-gray-200 bg-white dark:bg-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600 transition-colors group">
                   <svg class="w-8 h-8 mr-3 text-gray-400 group-hover:text-black dark:group-hover:text-white transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" /></svg>
                  <div class="text-left">
                      <div class="text-xs text-gray-500 uppercase font-semibold">Format</div>
                      <div class="text-base font-bold">Markdown</div>
                  </div>
                </button>
              </div>
          </div>
      </div>
    </main>
    
    <ConfirmationModal
      :is-open="showDeleteModal"
      title="Remove Key"
      message="Are you sure you want to remove this API key? This action cannot be undone."
      confirm-text="Remove"
      @confirm="confirmDeleteKey"
      @cancel="showDeleteModal = false"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useAuthStore } from '../stores/auth';
import { useRouter } from 'vue-router';
import api from '../services/api';
import NavBar from '../components/NavBar.vue';
import ThemeToggle from '../components/ThemeToggle.vue';
import ConfirmationModal from '../components/ConfirmationModal.vue';
import { useToast } from 'vue-toastification';

const authStore = useAuthStore();
const router = useRouter();
const toast = useToast();

const activeTab = ref('general');
const keys = ref([]);
const settings = ref({ auto_approve: true });
const newKey = ref({
  provider: 'openai',
  api_key: '',
  permissions: { read: true, write: false, auto_save: false }
});
const tokenCopied = ref(false);

const loadSettings = async () => {
  try {
    const res = await api.get('/user/settings');
    settings.value = { ...settings.value, ...res.data };
  } catch (err) {
    console.error(err);
  }
};

const toggleAutoApprove = async () => {
  const newVal = !settings.value.auto_approve;
  settings.value.auto_approve = newVal;
  try {
    await api.patch('/user/settings', { auto_approve: newVal });
    toast.success("Settings updated");
  } catch (err) {
    settings.value.auto_approve = !newVal; // revert
    toast.error("Failed to update settings");
  }
};

const loadKeys = async () => {
  try {
    const res = await api.get('/user/llm-keys');
    keys.value = res.data;
  } catch (err) {
    console.error(err);
  }
};

const addKey = async () => {
  if (!newKey.value.api_key) return toast.error("API Key required");
  try {
    await api.post('/user/llm-keys', newKey.value);
    toast.success("Key added");
    newKey.value.api_key = ""; // clear
    loadKeys();
  } catch (err) {
    toast.error("Failed to add key");
  }
};

const keyToDelete = ref(null);
const showDeleteModal = ref(false);

const deleteKey = (id) => {
  keyToDelete.value = id;
  showDeleteModal.value = true;
};

const confirmDeleteKey = async () => {
    if (!keyToDelete.value) return;
    try {
        await api.delete(`/user/llm-keys/${keyToDelete.value}`);
        toast.success("Key removed");
        loadKeys();
    } catch (err) {
        toast.error("Failed to remove key");
    } finally {
        showDeleteModal.value = false;
        keyToDelete.value = null;
    }
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

const copyToken = async () => {
  if (!authStore.token) {
    return toast.error("No token available");
  }
  try {
    await navigator.clipboard.writeText(authStore.token);
    tokenCopied.value = true;
    toast.success("Token copied");
    setTimeout(() => {
      tokenCopied.value = false;
    }, 2000);
  } catch (err) {
    toast.error("Failed to copy token");
  }
};

const restartTour = () => {
    localStorage.removeItem('tour_completed');
    toast.info("Tour reset. Returning to Dashboard...");
    setTimeout(() => router.push('/'), 1000);
};

// Initial load
loadKeys();
loadSettings();
</script>

<style scoped>
.animate-fade-in {
    animation: fadeIn 0.3s ease-in-out;
}
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(5px); }
    to { opacity: 1; transform: translateY(0); }
}
</style>
