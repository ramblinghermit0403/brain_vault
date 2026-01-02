<template>
  <div class="h-screen flex flex-col bg-gray-50 dark:bg-app transition-colors duration-300 font-sans overflow-hidden">

    <!-- Editor Header (Title & Actions) -->
    <header class="h-16 shrink-0 border-b border-gray-200 dark:border-border flex items-center justify-between px-6 bg-white dark:bg-surface relative z-10">
       <div class="flex items-center gap-4 flex-1">
          <button @click="goBack" class="text-gray-400 hover:text-gray-700 dark:text-gray-500 dark:hover:text-gray-300 transition-colors">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" /></svg>
          </button>
          <div class="flex items-center gap-3 w-full max-w-2xl">
              <span class="text-lg font-bold text-gray-900 dark:text-text-primary whitespace-nowrap">
                {{ isViewMode ? 'View Memory' : (documentId === 'new' ? 'New Memory' : 'Edit Memory') }}
              </span>
              <div class="h-6 w-px bg-gray-200 dark:bg-gray-600"></div>
              <input 
                v-model="title" 
                :readonly="isViewMode"
                class="bg-transparent border border-transparent focus:border-gray-300 dark:focus:border-gray-600 hover:border-gray-200 dark:hover:border-gray-700 rounded px-2 py-1 text-sm text-gray-600 dark:text-gray-300 w-full transition-colors"
                :class="{ 'cursor-default': isViewMode }"
                placeholder="Document Title"
              />
          </div>
       </div>
       <div class="flex items-center gap-3">
           <span v-if="saving" class="text-xs text-gray-400 animate-pulse">Saving...</span>
           <span v-else-if="lastSaved" class="text-xs text-gray-400">Saved {{ lastSaved }}</span>
           <button 
             v-if="documentId !== 'new'"
             @click="deleteDocument"
             class="p-2 text-red-600 hover:bg-red-50 dark:text-red-400 dark:hover:bg-red-900/20 rounded-md transition-colors"
             title="Delete Memory"
           >
             <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" /></svg>
           </button>
           <button 
             v-if="isInboxItem"
             @click="approveDocument"
             class="px-4 py-2 bg-green-600 hover:bg-green-700 text-white text-sm font-medium rounded-md transition-colors mr-2"
           >
             Approve
           </button>
            <button 
              v-if="isViewMode"
              @click="isViewMode = false"
              class="px-4 py-2 bg-black dark:bg-white text-white dark:text-black text-sm font-medium rounded-md transition-colors hover:bg-gray-900 dark:hover:bg-gray-200"
            >
              Edit
            </button>
            <button 
              v-if="!isViewMode"
              @click="saveDocument"
              :disabled="saving"
              class="px-4 py-2 bg-black dark:bg-white text-white dark:text-black text-sm font-medium rounded-md transition-colors hover:bg-gray-900 dark:hover:bg-gray-200"
            >
              Save Changes
            </button>
            <button 
              v-if="!isViewMode && documentId !== 'new'"
              @click="isViewMode = true"
              class="px-4 py-2 border border-gray-200 dark:border-border text-gray-600 dark:text-text-secondary text-sm font-medium rounded-md transition-colors hover:bg-gray-50 dark:hover:bg-gray-800"
            >
              Cancel
            </button>
       </div>
    </header>

    <!-- Toolbar (Functional) -->
    <div class="h-10 shrink-0 border-b border-gray-100 dark:border-gray-800 bg-gray-50/50 dark:bg-surface/50 flex items-center px-6 gap-4 overflow-x-auto"
         :class="{ 'opacity-50 pointer-events-none grayscale': isViewMode }">
        <div class="flex items-center gap-1 text-gray-500 dark:text-text-secondary">
            <button @click="insertText('**', '**')" class="p-1.5 hover:bg-gray-200 dark:hover:bg-gray-700 rounded transition-colors" title="Bold (Markdown **)">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 4h8a4 4 0 014 4 4 4 0 01-4 4H6V4zm0 8h9a5 5 0 015 5 5 5 0 01-5 5H6v-10z" /></svg>
            </button>
            <button @click="insertText('*', '*')" class="p-1.5 hover:bg-gray-200 dark:hover:bg-gray-700 rounded transition-colors" title="Italic (Markdown *)">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" /></svg>
            </button>
             <button @click="insertText('<u>', '</u>')" class="p-1.5 hover:bg-gray-200 dark:hover:bg-gray-700 rounded transition-colors" title="Underline">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 5v14M5 19h14" /></svg>
            </button>
        </div>
        <div class="h-4 w-px bg-gray-300 dark:bg-gray-600"></div>
        <div class="flex items-center gap-1 text-gray-500 dark:text-text-secondary">
            <button @click="insertText('- ')" class="p-1.5 hover:bg-gray-200 dark:hover:bg-gray-700 rounded transition-colors" title="List">
                 <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" /></svg>
            </button>
             <button @click="insertText('[', '](url)')" class="p-1.5 hover:bg-gray-200 dark:hover:bg-gray-700 rounded transition-colors" title="Link">
                 <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" /></svg>
            </button>
             <button @click="insertText('![alt](', ')')" class="p-1.5 hover:bg-gray-200 dark:hover:bg-gray-700 rounded transition-colors" title="Image">
                 <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" /></svg>
            </button>
        </div>
         <div class="h-4 w-px bg-gray-300 dark:bg-gray-600"></div>
          <div class="flex items-center gap-1 text-gray-500 dark:text-text-secondary">
             <button @click="insertText('```\n', '\n```')" class="p-1.5 hover:bg-gray-200 dark:hover:bg-gray-700 rounded transition-colors" title="Code Block">
                 <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" /></svg>
            </button>
          </div>
    </div>

    <!-- Main Content Area with Absolute Centering and Fixed Sidebar -->
    <div class="flex-1 overflow-hidden bg-gray-50 dark:bg-app relative flex flex-col">
        <!-- Main Document Container - Absolutely Centered -->
        <div class="w-full h-full overflow-y-auto flex justify-center p-4 sm:p-8">
             <div class="w-full max-w-4xl bg-white dark:bg-surface shadow-sm border border-gray-100 dark:border-border rounded-xl min-h-[calc(100vh-8rem)] flex flex-col p-8 sm:p-12 relative h-fit mb-12">
                <vue-monaco-editor
                  v-model:value="content"
                  theme="vs-light"
                  :options="editorOptions"
                  @mount="handleEditorMount"
                  language="markdown"
                  class="h-full w-full min-h-[500px]"
                />
            </div>
        </div>

        <!-- Fixed Right Sidebar -->
        <aside class="w-72 fixed right-0 top-16 bottom-0 overflow-y-auto border-l border-gray-100 dark:border-border bg-white dark:bg-surface hidden lg:block z-20 shadow-[min(0px)_0px_0px_0px_rgba(0,0,0,0.1)]">
             <div class="p-8 space-y-8">
                 <!-- Metadata Section -->
                <div>
                    <h4 class="text-[11px] font-bold text-gray-900 dark:text-gray-100 uppercase tracking-wider mb-6 pb-2 border-b border-gray-100 dark:border-gray-800">Properties</h4>
                    <div class="space-y-5">
                        <div class="grid grid-cols-[80px_1fr] items-center gap-2">
                            <label class="text-[11px] text-gray-500 font-medium">Created</label>
                            <p class="text-xs text-gray-900 dark:text-gray-200 font-medium truncate">{{ formatDate(docMetadata.created_at) }}</p>
                        </div>
                        <div class="grid grid-cols-[80px_1fr] items-center gap-2">
                            <label class="text-[11px] text-gray-500 font-medium">Source</label>
                            <div>
                                <span class="inline-flex items-center px-2 py-1 rounded-md text-[10px] font-medium bg-gray-50 dark:bg-gray-800 text-gray-700 dark:text-gray-300 border border-gray-200 dark:border-gray-700">
                                    {{ docMetadata.source_llm || 'User' }}
                                </span>
                            </div>
                        </div>
                        <div class="grid grid-cols-[80px_1fr] items-center gap-2">
                             <label class="text-[11px] text-gray-500 font-medium">Status</label>
                             <div class="flex items-center gap-1.5">
                                <span class="w-1.5 h-1.5 rounded-full" :class="docMetadata.status === 'approved' ? 'bg-green-500' : 'bg-yellow-500'"></span>
                                <span class="text-xs font-medium capitalize" :class="docMetadata.status === 'approved' ? 'text-green-700 dark:text-green-400' : 'text-yellow-700 dark:text-yellow-400'">
                                    {{ docMetadata.status || 'Active' }}
                                </span>
                             </div>
                        </div>
                    </div>
                </div>

                <!-- Tags Section -->
                <div>
                    <div class="flex items-center justify-between mb-4 pb-2 border-b border-gray-100 dark:border-gray-800">
                        <h4 class="text-[11px] font-bold text-gray-900 dark:text-gray-100 uppercase tracking-wider">Tags</h4>
                         <button 
                          @click="generateTags" 
                          :disabled="generatingTags || !content || isViewMode"
                          class="p-1 rounded hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors text-indigo-600 dark:text-indigo-400 disabled:opacity-30 disabled:hover:bg-transparent"
                          title="Auto-generate tags"
                        >
                             <svg v-if="generatingTags" class="animate-spin h-3.5 w-3.5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
                            <svg v-else class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>
                        </button>
                    </div>

                    <!-- View Mode Tags -->
                    <div v-if="isViewMode" class="flex flex-wrap gap-2">
                        <span v-for="tag in docMetadata.tags" :key="tag" class="px-2.5 py-1 bg-gray-50 dark:bg-gray-800 text-gray-600 dark:text-gray-300 rounded-md text-[11px] font-medium border border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600 transition-colors">
                            #{{ tag }}
                        </span>
                        <span v-if="!docMetadata.tags || !docMetadata.tags.length" class="text-[11px] text-gray-400 italic px-1">No tags added</span>
                    </div>

                    <!-- Edit Mode Tags Input -->
                    <div v-else class="space-y-3">
                        <div class="relative group">
                            <textarea 
                              v-model="tags" 
                              @input="handleTagInput"
                              @blur="hideSuggestionsWithDelay"
                              @keydown.down.prevent="navigateSuggestions(1)"
                              @keydown.up.prevent="navigateSuggestions(-1)"
                              @keydown.enter.prevent="selectActiveSuggestion"
                              class="w-full bg-gray-50 dark:bg-app border border-gray-200 dark:border-gray-700 rounded-lg px-3 py-2.5 text-xs focus:ring-1 focus:ring-black dark:focus:ring-white focus:border-black dark:focus:border-white outline-none transition-all placeholder:text-gray-400 dark:placeholder:text-gray-600 resize-none h-28 leading-relaxed"
                              placeholder="Enter tags separated by commas..."
                            ></textarea>
                            
                             <!-- Tag Suggestions -->
                            <div v-if="filteredSuggestions.length > 0 && showSuggestions" class="absolute bottom-full left-0 w-full mb-1 bg-white dark:bg-surface border border-gray-200 dark:border-gray-700 rounded-lg shadow-lg z-50 max-h-48 overflow-y-auto overflow-x-hidden">
                                <div 
                                  v-for="(suggestion, index) in filteredSuggestions" 
                                  :key="suggestion"
                                  @click="addTag(suggestion)"
                                   :class="['px-3 py-2 text-xs cursor-pointer transition-colors border-b border-gray-50 dark:border-gray-800 last:border-0', activeSuggestionIndex === index ? 'bg-gray-100 dark:bg-gray-800 text-black dark:text-white font-medium' : 'text-gray-600 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800']"
                                >
                                    #{{ suggestion }}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
             </div>
        </aside>
    </div>


    <ConfirmationModal
      :is-open="showDeleteModal"
      title="Delete Memory"
      message="Are you sure you want to delete this memory? This cannot be undone."
      confirm-text="Delete"
      @confirm="confirmDeleteDocument"
      @cancel="showDeleteModal = false"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, shallowRef } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { VueMonacoEditor } from '@guolao/vue-monaco-editor';
import { useToast } from 'vue-toastification';
import api from '../services/api';
import { useThemeStore } from '../stores/theme';
import NavBar from '../components/NavBar.vue';
import ConfirmationModal from '../components/ConfirmationModal.vue';

const route = useRoute();
const router = useRouter();
const themeStore = useThemeStore();
const toast = useToast();

const isInboxItem = ref(false);

const title = ref('');
const content = ref('');
const tags = ref('');
const allTags = ref([]);
const filteredSuggestions = ref([]);
const showSuggestions = ref(false);
const activeSuggestionIndex = ref(-1);

const saving = ref(false);
const lastSaved = ref(null);
const isViewMode = ref(route.params.id !== 'new');
const documentId = computed(() => route.params.id);
const docMetadata = ref({});
const editorInstance = shallowRef(null);

const fetchTags = async () => {
    try {
        const response = await api.get('/memory/tags');
        allTags.value = response.data;
    } catch (e) {
        console.error('Failed to fetch tags', e);
    }
};

const generatingTags = ref(false);

const generateTags = async () => {
    if (!content.value) return;
    generatingTags.value = true;
    try {
        const currentTags = tags.value.split(',').map(t => t.trim()).filter(Boolean);
        
        const response = await api.post('/llm/suggest_tags', {
            content: content.value,
            existing_tags: allTags.value
        });
        
        const suggested = response.data;
        if (suggested && suggested.length > 0) {
            const newTags = [...new Set([...currentTags, ...suggested])];
            tags.value = newTags.join(', ') + ', ';
        } else {
            toast.info('No new tags suggested');
        }
    } catch (e) {
        console.error('Auto-tag failed', e);
        toast.error('Failed to generate tags. Please check your API key in Settings.');
    } finally {
        generatingTags.value = false;
    }
};

const handleTagInput = () => {
    const parts = tags.value.split(',');
    const currentInput = parts[parts.length - 1].trim().toLowerCase();
    
    if (!currentInput) {
        showSuggestions.value = false;
        return;
    }
    
    const usedTags = parts.slice(0, -1).map(t => t.trim().toLowerCase());
    
    filteredSuggestions.value = allTags.value.filter(tag => 
        tag.toLowerCase().includes(currentInput) && 
        !usedTags.includes(tag.toLowerCase()) &&
        tag.toLowerCase() !== currentInput // Don't suggest exact match if already typed
    ).slice(0, 5);
    
    showSuggestions.value = filteredSuggestions.value.length > 0;
    activeSuggestionIndex.value = -1;
};

const addTag = (tag) => {
    const parts = tags.value.split(',');
    parts.pop(); // Remove partial
    parts.push(` ${tag}`);
    tags.value = parts.join(',') + ', ';
    showSuggestions.value = false;
};

const hideSuggestionsWithDelay = () => {
    setTimeout(() => {
        showSuggestions.value = false;
    }, 200);
};

const navigateSuggestions = (direction) => {
    if (!showSuggestions.value) return;
    const len = filteredSuggestions.value.length;
    activeSuggestionIndex.value = (activeSuggestionIndex.value + direction + len) % len;
};

const selectActiveSuggestion = () => {
    if (showSuggestions.value && activeSuggestionIndex.value >= 0) {
        addTag(filteredSuggestions.value[activeSuggestionIndex.value]);
    }
};

const editorOptions = computed(() => ({
  automaticLayout: true,
  minimap: { enabled: false },
  wordWrap: 'on',
  fontSize: 15,
  fontFamily: 'Inter, sans-serif',
  theme: themeStore.isDark ? 'vs-dark' : 'vs-light',
  lineNumbers: 'off',
  padding: { top: 16, bottom: 16 },
  overviewRulerLanes: 0,
  hideCursorInOverviewRuler: true,
  scrollbar: {
      vertical: 'hidden',
      horizontal: 'hidden'
  },
  scrollBeyondLastLine: false,
  readOnly: isViewMode.value,
}));

const handleEditorMount = (editor) => {
  editorInstance.value = editor;
  if (themeStore.isDark) {
    // Force dark theme if needed, usually handled by prop
  }
};

const insertText = (prefix, suffix = '') => {
  const editor = editorInstance.value;
  if (!editor) return;

  const selection = editor.getSelection();
  const text = editor.getModel().getValueInRange(selection);
  const newText = prefix + text + suffix;

  editor.executeEdits('toolbar', [{
    range: selection,
    text: newText,
    forceMoveMarkers: true
  }]);
  
  editor.focus();
};

const resolvedId = ref(null);

const fetchDocument = async () => {
  try {
    if (documentId.value === 'new') return;

    // 1. Try fetching from Memory List
    let found = false;
    try {
        const response = await api.get('/memory/');
        let doc = response.data.find(d => String(d.id) === String(documentId.value));
        if (!doc) {
           const numericId = String(documentId.value).split('_').pop();
           doc = response.data.find(d => String(d.id).endsWith(`_${numericId}`));
        }
        
        if (doc) {
            resolvedId.value = doc.id;
            title.value = doc.title;
            content.value = doc.content || '';
            tags.value = Array.isArray(doc.tags) ? doc.tags.join(', ') : (doc.tags || '');
            docMetadata.value = {
                created_at: doc.created_at,
                source_llm: doc.source_llm,
                status: doc.status,
                tags: doc.tags
            };
            isInboxItem.value = false;
            found = true;
        }
    } catch (e) { console.debug('Not in memory list', e); }

    // 2. If not found, try Inbox
    if (!found) {
        try {
            const inboxRes = await api.get(`/inbox/${documentId.value}`);
            if (inboxRes.data) {
                const doc = inboxRes.data;
                resolvedId.value = doc.id;
                title.value = doc.details || 'Untitled';
                content.value = doc.content || '';
                tags.value = Array.isArray(doc.tags) ? doc.tags.join(', ') : (doc.tags || '');
                docMetadata.value = {
                    created_at: doc.created_at,
                    source_llm: doc.source_llm,
                    status: 'pending',
                    tags: doc.tags
                };
                isInboxItem.value = true;
                found = true;
            }
        } catch (e) {
             console.debug('Not in inbox', e);
        }
    }

    if (!found) {
        router.push('/');
    }

  } catch (error) {
    console.error('Error fetching document:', error);
  }
};

const saveDocument = async () => {
  if (!title.value) return;
  
  saving.value = true;
  try {
    const tagsList = tags.value.split(',').map(t => t.trim()).filter(t => t);
    
    if (documentId.value === 'new') {
      const response = await api.post('/memory/', {
        title: title.value,
        content: content.value,
        tags: tagsList
      });
      router.replace(`/editor/mem_${response.data.id}`);
    } else {
      const targetId = resolvedId.value || documentId.value;
      
      if (isInboxItem.value) {
           await api.put(`/inbox/${targetId}`, {
              title: title.value,
              content: content.value
          });
      } else {
          await api.put(`/memory/${targetId}`, {
              title: title.value,
              content: content.value,
              tags: tagsList
          });
      }
    }
    toast.success('Memory saved successfully');
    lastSaved.value = new Date().toLocaleTimeString();
    isViewMode.value = true;
    fetchDocument(); // Refresh metadata
  } catch (error) {
    console.error('Error saving document:', error);
    toast.error('Failed to save memory');
  } finally {
    saving.value = false;
  }
};

const approveDocument = async () => {
    if (!confirm('Approve this pending item and move to memory?')) return;
    try {
        const targetId = resolvedId.value || documentId.value;
        await api.post(`/inbox/${targetId}/action`, { action: 'approve' });
        toast.success('Document approved');
        router.push('/inbox');
    } catch (e) {
        console.error('Failed to approve', e);
        toast.error('Failed to approve document');
    }
};

const showDeleteModal = ref(false);

const deleteDocument = async () => {
  if (documentId.value === 'new') {
    router.push('/');
    return;
  }
  showDeleteModal.value = true;
};

const confirmDeleteDocument = async () => {
  try {
    const targetId = resolvedId.value || documentId.value;
    // Handle 'mem_' prefix if present in ID but API expects int, or vice versa.
    // Usually API takes the ID passed.
    await api.delete(`/memory/${targetId}`);
    toast.success('Document deleted');
    router.push('/');
  } catch (error) {
    console.error('Error deleting document:', error);
    toast.error('Failed to delete document'); // Simple feedback
  } finally {
    showDeleteModal.value = false;
  }
};

const formatDate = (dateString) => {
  if (!dateString) return 'Unknown';
  try {
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
  } catch (e) {
    return 'Invalid Date';
  }
};

const goBack = () => {
  router.go(-1);
};

// Auto-save every 30 seconds if changed
// Auto-save disabled by user request
onMounted(() => {
  fetchDocument();
  fetchTags();
});

onUnmounted(() => {
  // cleanup
});

</script>
