<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900 flex flex-col">
    <!-- Header -->
    <NavBar />

    <main class="flex-1 max-w-7xl mx-auto w-full px-4 sm:px-6 lg:px-8 py-8">
      <div class="mb-8">
         <h1 class="text-3xl font-bold text-gray-900 dark:text-white">Universal Prompt Engine</h1>
      </div>

      <div class="flex flex-col lg:flex-row gap-8">
        <!-- Left Panel: Controls -->
        <div class="w-full lg:w-1/3 space-y-6">
        <div class="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
          <h2 class="text-lg font-medium text-gray-900 dark:text-white mb-4">Configuration</h2>
          
          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Topic / Query</label>
              <textarea 
                v-model="query" 
                rows="4" 
                class="w-full rounded-md border-gray-300 dark:border-gray-600 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                placeholder="What do you want to ask the LLM?"
              ></textarea>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Template</label>
              <select v-model="templateId" class="w-full rounded-md border-gray-300 dark:border-gray-600 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white">
                <option value="standard">Standard (Q&A)</option>
                <option value="code">Code Assistant</option>
                <option value="summary">Summarization</option>
              </select>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Context Size (Tokens): {{ contextSize }}
              </label>
              <input 
                type="range" 
                v-model.number="contextSize" 
                min="500" 
                max="4000" 
                step="100" 
                class="w-full"
              >
            </div>

            <button 
              @click="generatePrompt" 
              :disabled="!query || loading"
              class="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
            >
              <span v-if="loading">Generating...</span>
              <span v-else>Generate Prompt</span>
            </button>
          </div>
        </div>

        <!-- Provenance -->
        <div v-if="contextUsed.length > 0" class="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
          <h2 class="text-lg font-medium text-gray-900 dark:text-white mb-4">Context Used</h2>
          <ul class="space-y-2 max-h-60 overflow-y-auto custom-scrollbar">
            <li v-for="(ctx, idx) in contextUsed" :key="idx" class="text-xs text-gray-600 dark:text-gray-400 bg-gray-50 dark:bg-gray-700 p-2 rounded border border-gray-200 dark:border-gray-600">
              {{ ctx.substring(0, 100) }}...
            </li>
          </ul>
        </div>
      </div>

      <!-- Right Panel: Output -->
      <div class="w-full lg:w-2/3">
        <div class="bg-white dark:bg-gray-800 shadow rounded-lg p-6 h-full flex flex-col">
          <div class="flex justify-between items-center mb-4">
            <h2 class="text-lg font-medium text-gray-900 dark:text-white">Generated Prompt</h2>
            <button 
              v-if="generatedPrompt"
              @click="copyToClipboard" 
              class="inline-flex items-center px-3 py-1.5 border border-gray-300 dark:border-gray-600 shadow-sm text-xs font-medium rounded text-gray-700 dark:text-gray-200 bg-white dark:bg-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600"
            >
              <span v-if="copied">Copied!</span>
              <span v-else>Copy to Clipboard</span>
            </button>
          </div>
          
          <div class="flex-1 relative">
            <textarea 
              readonly
              v-model="generatedPrompt"
              class="w-full h-full min-h-[500px] p-4 rounded-md border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-gray-100 font-mono text-sm resize-none focus:ring-0 focus:border-gray-300 dark:focus:border-gray-600"
              placeholder="Your generated prompt will appear here..."
            ></textarea>
          </div>
          
          <div v-if="generatedPrompt" class="mt-2 text-right text-xs text-gray-500 dark:text-gray-400">
            Total Tokens: {{ tokenCount }}
          </div>
        </div>
      </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import api from '../services/api';
import { useToast } from 'vue-toastification';
import NavBar from '../components/NavBar.vue';

const query = ref('');
const templateId = ref('standard');
const contextSize = ref(2000);
const loading = ref(false);
const generatedPrompt = ref('');
const contextUsed = ref([]);
const tokenCount = ref(0);
const copied = ref(false);
const toast = useToast();

const generatePrompt = async () => {
  loading.value = true;
  generatedPrompt.value = '';
  contextUsed.value = [];
  
  try {
    const response = await api.post('/prompts/generate', {
      query: query.value,
      template_id: templateId.value,
      context_size: contextSize.value
    });
    
    generatedPrompt.value = response.data.prompt;
    contextUsed.value = response.data.context_used;
    tokenCount.value = response.data.token_count;
  } catch (error) {
    console.error('Error generating prompt:', error);
    toast.error('Failed to generate prompt');
  } finally {
    loading.value = false;
  }
};

const copyToClipboard = async () => {
  try {
    await navigator.clipboard.writeText(generatedPrompt.value);
    copied.value = true;
    setTimeout(() => copied.value = false, 2000);
    toast.success('Prompt copied to clipboard');
  } catch (err) {
    console.error('Failed to copy:', err);
    toast.error('Failed to copy prompt');
  }
};
</script>
