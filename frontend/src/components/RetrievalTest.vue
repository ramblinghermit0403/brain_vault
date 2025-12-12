<template>
  <div :class="['flex flex-col h-full bg-white dark:bg-gray-800 transition-all duration-200', !embedded ? 'shadow-lg rounded-xl border border-gray-100 dark:border-gray-700' : '']">
    
    <!-- Header (only if not embedded) -->
    <div v-if="!embedded" class="p-6 border-b border-gray-100 dark:border-gray-700 flex items-center">
        <div class="h-10 w-10 rounded-full bg-green-100 dark:bg-green-900 flex items-center justify-center mr-4">
          <svg class="h-6 w-6 text-green-600 dark:text-green-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        </div>
        <div>
          <h3 class="text-lg font-bold text-gray-900 dark:text-white">Ask Your Brain Vault</h3>
          <p class="text-sm text-gray-500 dark:text-gray-400">Retrieve information from your documents</p>
        </div>
    </div>
      
    <!-- Content -->
    <div :class="['flex-1 flex flex-col space-y-4', embedded ? '' : 'p-6']">
      
      <!-- Input Area -->
      <div class="relative group">
        <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
           <svg class="h-5 w-5 text-gray-400 group-focus-within:text-green-500 transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor">
               <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
           </svg>
        </div>
        <input 
          type="text" 
          v-model="query" 
          @keyup.enter="search" 
          :disabled="loading"
          class="block w-full pl-10 pr-12 py-3 bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl focus:ring-2 focus:ring-green-500 focus:border-transparent transition-all placeholder-gray-400 text-sm"
          placeholder="Ask a question..." 
        />
        <div class="absolute inset-y-0 right-0 flex items-center pr-2">
             <select v-model="provider" class="h-8 text-xs bg-transparent border-0 text-gray-400 focus:ring-0 cursor-pointer hover:text-gray-600 dark:hover:text-gray-300">
                <option value="gemini">Gemini</option>
                <option value="openai">GPT-3.5</option>
             </select>
        </div>
      </div>
      
      <!-- Loading State -->
      <div v-if="loading" class="flex items-center justify-center py-8">
          <div class="flex space-x-1 animate-pulse">
              <div class="w-2 h-2 bg-green-500 rounded-full"></div>
              <div class="w-2 h-2 bg-green-500 rounded-full animation-delay-200"></div>
              <div class="w-2 h-2 bg-green-500 rounded-full animation-delay-400"></div>
          </div>
          <span class="ml-3 text-sm text-gray-400 font-medium">Thinking...</span>
      </div>

      <!-- Response Area -->
      <div v-if="response && !loading" class="bg-gray-50 dark:bg-gray-700/30 rounded-xl p-4 border border-gray-100 dark:border-gray-700/50 animate-fade-in">
        <div class="flex items-center justify-between mb-2">
            <span class="text-xs font-semibold text-green-600 dark:text-green-400 uppercase tracking-wide">
                {{ provider === 'gemini' ? 'Gemini' : 'OpenAI' }} Says
            </span>
             <button @click="response = ''" class="text-gray-400 hover:text-gray-600">
                <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
            </button>
        </div>
        <div class="text-gray-700 dark:text-gray-300 text-sm leading-relaxed prose dark:prose-invert max-w-none">
          {{ response }}
        </div>
        
        <!-- Sources -->
        <div v-if="context && context.length" class="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700 border-dashed">
            <p class="text-xs text-gray-400 mb-2 font-medium">Sources:</p>
            <div class="space-y-2">
                <div v-for="(ctx, idx) in context.slice(0, 2)" :key="idx" class="text-[10px] bg-white dark:bg-gray-800 p-2 rounded border border-gray-100 dark:border-gray-700 text-gray-500 truncate">
                    {{ ctx }}
                </div>
            </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import api from '../services/api';

const props = defineProps({
  embedded: {
    type: Boolean,
    default: false
  }
});

const query = ref('');
const loading = ref(false);
const response = ref('');
const context = ref([]);
const provider = ref('gemini');

const search = async () => {
  if (!query.value) return;

  loading.value = true;
  response.value = '';
  context.value = [];

  try {
    const apiKey = provider.value === 'gemini' 
      ? localStorage.getItem('gemini_key') 
      : localStorage.getItem('openai_key');

    if (!apiKey) {
      response.value = `Error: Please set your ${provider.value === 'gemini' ? 'Gemini' : 'OpenAI'} API key in Settings.`;
      loading.value = false;
      return;
    }

    const res = await api.post('/llm/chat', {
      query: query.value,
      provider: provider.value,
      api_key: apiKey,
      top_k: 3
    });
    
    response.value = res.data.response;
    context.value = res.data.context;
  } catch (error) {
    response.value = 'Error: ' + (error.response?.data?.detail || error.message);
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.animation-delay-200 { animation-delay: 0.2s; }
.animation-delay-400 { animation-delay: 0.4s; }
.animate-fade-in { animation: fadeIn 0.3s ease-out forwards; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(5px); } to { opacity: 1; transform: translateY(0); } }
</style>
