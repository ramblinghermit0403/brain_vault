<template>
  <div class="h-screen flex flex-col bg-white dark:bg-gray-900">
    <!-- Toolbar -->
    <header class="h-auto min-h-14 border-b border-gray-200 dark:border-gray-700 flex flex-col justify-center px-4 bg-white dark:bg-gray-800 py-2 space-y-2">
      <div class="flex items-center justify-between w-full">
        <div class="flex items-center space-x-4 flex-1">
          <button @click="goBack" class="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
          </button>
          <input 
            v-model="title" 
            class="bg-transparent border-none focus:ring-0 text-lg font-medium text-gray-900 dark:text-white placeholder-gray-400 w-full"
            placeholder="Document Title"
          />
        </div>
        <div class="flex items-center space-x-3 shrink-0">
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
          <button 
            @click="toggleSidebar" 
            class="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 rounded-md hover:bg-gray-100 dark:hover:bg-gray-700"
            title="Ask Question"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
            </svg>
          </button>
        </div>
      </div>
      
      <!-- Tags Input -->
      <div class="flex items-center space-x-2 pl-10 w-full">
        <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
        </svg>
        <input 
          v-model="tags" 
          class="bg-transparent border-none focus:ring-0 text-sm text-gray-600 dark:text-gray-300 placeholder-gray-400 w-full"
          placeholder="Add tags (comma separated)..."
        />
      </div>
    </header>

    <!-- Editor & Preview -->
    <div class="flex-1 flex overflow-hidden relative">
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

      <!-- Ask Question Sidebar -->
      <AskQuestionSidebar 
        :is-open="showSidebar" 
        :document-id="documentId" 
        type="document"
        @close="showSidebar = false"
      />
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
import AskQuestionSidebar from '../components/AskQuestionSidebar.vue';

const route = useRoute();
const router = useRouter();
const themeStore = useThemeStore();

const md = new MarkdownIt();

const title = ref('');
const content = ref('');
const tags = ref('');
const showPreview = ref(true);
const showSidebar = ref(false);
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

const resolvedId = ref(null);

const fetchDocument = async () => {
  try {
    if (documentId.value === 'new') return;

    // Use /memory/ endpoint which returns both memories and documents with tags
    const response = await api.get('/memory/');
    
    // Find by ID match (handling mem_123 and doc_123 prefixes)
    let doc = response.data.find(d => d.id === documentId.value);
    
    if (!doc) {
      // Fallback: try to find by numeric ID if prefix is missing in route or vice versa
      const numericId = documentId.value.split('_').pop();
      doc = response.data.find(d => d.id.endsWith(`_${numericId}`));
    }
    
    if (doc) {
      resolvedId.value = doc.id; // Store the full ID with prefix (e.g., doc_1, mem_1)
      title.value = doc.title;
      content.value = doc.content || '';
      tags.value = Array.isArray(doc.tags) ? doc.tags.join(', ') : (doc.tags || '');
    } else {
      console.error('Document not found in list');
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
    const tagsList = tags.value.split(',').map(t => t.trim()).filter(t => t);
    
    if (documentId.value === 'new') {
      const response = await api.post('/memory/', {
        title: title.value,
        content: content.value,
        tags: tagsList
      });
      // Redirect to edit page of new doc
      router.replace(`/editor/mem_${response.data.id}`);
    } else {
      // Use resolvedId if available, otherwise fallback to documentId
      const targetId = resolvedId.value || documentId.value;
      
      // Determine endpoint based on ID prefix
      const isDoc = targetId.startsWith('doc_');
      const id = targetId.split('_')[1] || targetId;
      
      if (isDoc) {
         await api.put(`/documents/${id}`, {
          title: title.value,
          content: content.value,
          tags: tagsList
        });
      } else {
        // Assume memory
        await api.put(`/memory/${targetId}`, {
          title: title.value,
          content: content.value,
          tags: tagsList
        });
      }
      console.log('Updated document:', targetId);
    }
    lastSaved.value = new Date().toLocaleTimeString();
  } catch (error) {
    console.error('Error saving document:', error);
    
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

const toggleSidebar = () => {
  showSidebar.value = !showSidebar.value;
};

const goBack = () => {
  router.push('/');
};

// Auto-save every 30 seconds if changed
let autoSaveInterval;
onMounted(() => {
  fetchDocument();
  autoSaveInterval = setInterval(() => {
    if (content.value && documentId.value && documentId.value !== 'new') {
        saveDocument();
    }
  }, 30000);
});

onUnmounted(() => {
  if (autoSaveInterval) clearInterval(autoSaveInterval);
});

watch(() => themeStore.isDark, (isDark) => {
  // Monaco theme update handled by computed options
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
