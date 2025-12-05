<template>
  <div 
    v-if="isOpen"
    class="fixed inset-y-0 right-0 w-96 bg-white dark:bg-gray-800 shadow-xl transform transition-transform duration-300 ease-in-out z-50 flex flex-col border-l border-gray-200 dark:border-gray-700"
    :class="isOpen ? 'translate-x-0' : 'translate-x-full'"
  >
    <!-- Header -->
    <div class="px-4 py-3 border-b border-gray-200 dark:border-gray-700 flex justify-between items-center bg-gray-50 dark:bg-gray-900">
      <h3 class="text-lg font-medium text-gray-900 dark:text-white flex items-center">
        <svg class="w-5 h-5 mr-2 text-indigo-600 dark:text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
        </svg>
        Ask Question
      </h3>
      <button @click="$emit('close')" class="text-gray-400 hover:text-gray-500 dark:hover:text-gray-300">
        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    </div>

    <!-- Chat Area -->
    <div class="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50 dark:bg-gray-900">
      <div v-for="(msg, index) in messages" :key="index" :class="['flex', msg.role === 'user' ? 'justify-end' : 'justify-start']">
        <div 
          :class="[
            'max-w-xs px-4 py-2 rounded-lg text-sm',
            msg.role === 'user' 
              ? 'bg-indigo-600 text-white rounded-br-none' 
              : 'bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-200 border border-gray-200 dark:border-gray-700 rounded-bl-none shadow-sm'
          ]"
        >
          <div class="whitespace-pre-wrap">{{ msg.content }}</div>
          <!-- Sources -->
          <div v-if="msg.context && msg.context.length" class="mt-3 pt-3 border-t border-gray-200 dark:border-gray-700">
            <p class="text-xs font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1">Sources:</p>
            <ul class="space-y-1">
              <li v-for="(ctx, ctxIdx) in msg.context" :key="ctxIdx" class="text-xs text-gray-600 dark:text-gray-300 bg-gray-100 dark:bg-gray-700 p-1.5 rounded">
                {{ ctx.substring(0, 100) }}...
              </li>
            </ul>
          </div>
        </div>
      </div>
      <div v-if="loading" class="flex justify-start">
        <div class="bg-white dark:bg-gray-800 px-4 py-2 rounded-lg rounded-bl-none border border-gray-200 dark:border-gray-700 shadow-sm">
          <div class="flex space-x-1">
            <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
            <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.2s"></div>
            <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.4s"></div>
          </div>
        </div>
      </div>
      <div ref="messagesEnd"></div>
    </div>

    <!-- Input Area -->
    <div class="p-4 border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 space-y-3">
      <!-- Provider Selection -->
      <div>
        <select v-model="selectedProvider" class="block w-full text-xs border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white">
          <option value="gemini">Google Gemini</option>
          <option value="openai">OpenAI (GPT-3.5)</option>
        </select>
      </div>

      <form @submit.prevent="sendMessage" class="flex space-x-2">
        <input 
          v-model="query" 
          type="text" 
          placeholder="Ask about this document..." 
          class="flex-1 border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
          :disabled="loading"
        />
        <button 
          type="submit" 
          :disabled="!query || loading"
          class="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
          </svg>
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, nextTick } from 'vue';
import api from '../services/api';

const props = defineProps({
  isOpen: Boolean,
  documentId: [String, Number],
  type: {
    type: String,
    default: 'document' // 'document' or 'memory'
  }
});

const emit = defineEmits(['close']);

const query = ref('');
const messages = ref([]);
const loading = ref(false);
const messagesEnd = ref(null);
const selectedProvider = ref('gemini');

const scrollToBottom = async () => {
  await nextTick();
  if (messagesEnd.value) {
    messagesEnd.value.scrollIntoView({ behavior: 'smooth' });
  }
};

const sendMessage = async () => {
  if (!query.value.trim()) return;

  const userMsg = query.value;
  messages.value.push({ role: 'user', content: userMsg });
  query.value = '';
  loading.value = true;
  scrollToBottom();

  try {
    // Determine filter based on ID format
    // If documentId starts with 'mem_', it's a memory. 'doc_' is a document.
    // Or use props.type.
    
    let filter = {};
    if (props.documentId) {
        // Assuming backend supports filtering by memory_id or document_id
        // For memories, we store "memory_id" in metadata.
        // For documents, we might need to check how they are stored.
        // In ingestion.py, we might need to see what metadata is stored.
        // But for now, let's assume standard metadata.
        
        // If ID is like "mem_123", extract 123.
        const idStr = props.documentId.toString();
        let realId = idStr;
        let type = props.type;
        
        if (idStr.startsWith('mem_')) {
            realId = parseInt(idStr.split('_')[1]);
            type = 'memory';
        } else if (idStr.startsWith('doc_')) {
            realId = parseInt(idStr.split('_')[1]);
            type = 'document';
        }

        if (type === 'memory') {
            filter = { "memory_id": realId };
        } else {
            // For documents, we usually store document_id in chunks
            // Let's check ingestion.py or document.py to be sure.
            // Assuming "document_id" is used.
            filter = { "document_id": realId };
        }
    }

    const provider = selectedProvider.value;
    const apiKey = provider === 'gemini' 
      ? localStorage.getItem('gemini_key') 
      : localStorage.getItem('openai_key');

    if (!apiKey) {
      messages.value.push({ role: 'assistant', content: `Error: Please set your ${provider === 'gemini' ? 'Gemini' : 'OpenAI'} API key in Settings.` });
      loading.value = false;
      return;
    }

    const res = await api.post('/llm/chat', {
      query: userMsg,
      provider: provider,
      api_key: apiKey,
      top_k: 5,
      filter: filter
    });

    messages.value.push({ 
      role: 'assistant', 
      content: res.data.response,
      context: res.data.context 
    });
  } catch (error) {
    console.error('Chat error:', error);
    messages.value.push({ role: 'assistant', content: 'Sorry, I encountered an error processing your request.' });
  } finally {
    loading.value = false;
    scrollToBottom();
  }
};

watch(() => props.isOpen, (newVal) => {
  if (newVal) {
    scrollToBottom();
  }
});
</script>
