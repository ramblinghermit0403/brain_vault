<template>
  <div class="h-screen flex flex-col bg-white dark:bg-gray-900">
    <!-- Toolbar -->
    <header class="h-14 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between px-4 bg-white dark:bg-gray-800">
      <div class="flex items-center space-x-4">
        <button @click="goBack" class="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200">
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
          </svg>
        </button>
        <input 
          v-model="title" 
          class="bg-transparent border-none focus:ring-0 text-lg font-medium text-gray-900 dark:text-white placeholder-gray-400"
          placeholder="Document Title"
        />
      </div>
      <div class="flex items-center space-x-3">
        <span v-if="saving" class="text-sm text-gray-500 dark:text-gray-400">Saving...</span>
        <span v-else-if="lastSaved" class="text-sm text-gray-500 dark:text-gray-400">Saved {{ lastSaved }}</span>
        <button 
          @click="saveDocument" 
          class="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-medium rounded-md transition-colors"
          :disabled="saving"
        >
          Save
        </button>
        <button 
          @click="togglePreview" 
          class="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 rounded-md hover:bg-gray-100 dark:hover:bg-gray-700"
          title="Toggle Preview"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
          </svg>
        </button>
      </div>
    </header>

    <!-- Editor & Preview -->
    <div class="flex-1 flex overflow-hidden">
      <!-- Editor Pane -->
      <div :class="['h-full transition-all duration-300', showPreview ? 'w-1/2 border-r border-gray-200 dark:border-gray-700' : 'w-full']">
        <vue-monaco-editor
          v-model:value="content"
          theme="vs-dark"
          :options="editorOptions"
          @mount="handleEditorMount"
          language="markdown"
          class="h-full w-full"
        />
      </div>

      <!-- Preview Pane -->
      <div v-if="showPreview" class="w-1/2 h-full overflow-auto bg-white dark:bg-gray-900 p-8 prose dark:prose-invert max-w-none">
        <div v-html="renderedContent"></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { VueMonacoEditor } from '@guolao/vue-monaco-editor';
import MarkdownIt from 'markdown-it';
import api from '../services/api';
import { useThemeStore } from '../stores/theme';

const route = useRoute();
const router = useRouter();
const themeStore = useThemeStore();

const md = new MarkdownIt();

const title = ref('');
const content = ref('');
const showPreview = ref(true);
const saving = ref(false);
const lastSaved = ref(null);
const documentId = computed(() => route.params.id);

const editorOptions = computed(() => ({
  automaticLayout: true,
  minimap: { enabled: false },
  wordWrap: 'on',
  fontSize: 14,
  theme: themeStore.isDark ? 'vs-dark' : 'vs',
  padding: { top: 16, bottom: 16 }
}));

const renderedContent = computed(() => md.render(content.value || ''));

const handleEditorMount = (editor) => {
  // editor instance available here
};

const fetchDocument = async () => {
  try {
    // If creating new document (id='new'), skip fetch
    if (documentId.value === 'new') return;

    // Currently we don't have a direct "get by id" that returns single doc details easily 
    // without filtering the list, but let's assume we can filter the list or add a specific endpoint.
    // For now, we'll fetch all and find it, or use the list endpoint if it supports filtering.
    // Ideally backend should have GET /documents/{id}
    
    // Let's try to fetch from the list first as a fallback or implement GET /documents/{id} in backend if missing.
    // Wait, we implemented GET /documents/ but not GET /documents/{id} specifically for retrieval?
    // Let's check backend... we have DELETE /documents/{id} and PUT /documents/{id}.
    // We should add GET /documents/{id} to backend for efficiency.
    
    // For now, let's assume we can get it from the list.
    const response = await api.get('/documents/');
    const doc = response.data.find(d => d.id.toString() === documentId.value);
    
    if (doc) {
      title.value = doc.title;
      content.value = doc.content || '';
    } else {
      alert('Document not found');
      router.push('/');
    }
  } catch (error) {
    console.error('Error fetching document:', error);
  }
};

const saveDocument = async () => {
  if (!title.value) {
    alert('Please enter a title');
    return;
  }
  
  saving.value = true;
  try {
    if (documentId.value === 'new') {
      const response = await api.post('/documents/memory', {
        title: title.value,
        content: content.value
      });
      console.log('Created memory:', response.data);
      // Redirect to edit page of new doc
      router.replace(`/editor/${response.data.document_id}`);
    } else {
      await api.put(`/documents/${documentId.value}`, {
        title: title.value,
        content: content.value
      });
      console.log('Updated document:', documentId.value);
    }
    lastSaved.value = new Date().toLocaleTimeString();
  } catch (error) {
    console.error('Error saving document:', error);
    
    // If 401, let the interceptor handle the redirect
    if (error.response && error.response.status === 401) return;
    
    let errorMessage = error.message;
    if (error.response?.data?.detail) {
      const detail = error.response.data.detail;
      if (typeof detail === 'object') {
        errorMessage = JSON.stringify(detail);
      } else {
        errorMessage = detail;
      }
    }
    
    alert('Failed to save: ' + errorMessage);
  } finally {
    saving.value = false;
  }
};

const togglePreview = () => {
  showPreview.value = !showPreview.value;
};

const goBack = () => {
  router.push('/');
};

// Auto-save every 30 seconds if changed
let autoSaveInterval;
onMounted(() => {
  fetchDocument();
  autoSaveInterval = setInterval(() => {
    // Only auto-save if we have content and a valid ID (not new, not undefined)
    if (content.value && documentId.value && documentId.value !== 'new') {
        saveDocument();
    }
  }, 30000);
});

onUnmounted(() => {
  if (autoSaveInterval) clearInterval(autoSaveInterval);
});

watch(() => themeStore.isDark, (isDark) => {
  // Monaco theme update handled by computed options, but might need explicit set
  // This depends on how the wrapper handles reactivity.
});

</script>

<style scoped>
/* Custom scrollbar for preview */
.prose::-webkit-scrollbar {
  width: 8px;
}
.prose::-webkit-scrollbar-track {
  background: transparent;
}
.prose::-webkit-scrollbar-thumb {
  background-color: #d1d5db; /* bg-gray-300 */
  border-radius: 0.25rem; /* rounded */
}
.dark .prose::-webkit-scrollbar-thumb {
  background-color: #4b5563; /* dark:bg-gray-600 */
}
</style>
