<template>
  <div v-if="isOpen" class="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6" role="dialog" aria-modal="true">
    
    <!-- Backdrop -->
    <div class="fixed inset-0 bg-gray-900/40 backdrop-blur-sm transition-opacity" @click="close"></div>

    <!-- Modal Panel -->
    <div class="relative w-[700px] h-[600px] overflow-hidden rounded-xl bg-white dark:bg-zinc-900 text-left shadow-2xl transition-all flex flex-col">
      
      <!-- Close Button -->
      <button @click="close" class="absolute top-4 right-4 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors z-10">
        <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>

      <!-- Header -->
      <div class="px-8 pt-8 pb-4">
        <h3 class="text-2xl font-bold text-gray-900 dark:text-white mb-1">Add Content</h3>
        <p class="text-gray-500 dark:text-gray-400 text-sm">Choose a method to add content to your Brain Vault.</p>
      </div>

      <!-- Tabs -->
      <div class="px-8 mb-6">
        <div class="flex bg-gray-100 dark:bg-zinc-800 p-1 rounded-lg overflow-x-auto">
          <button 
            v-for="tab in tabs" 
            :key="tab.id"
            @click="activeTab = tab.id"
            :class="[
              'flex-1 flex items-center justify-center gap-2 py-2 text-sm font-medium rounded-md transition-all whitespace-nowrap px-3',
              activeTab === tab.id 
                ? 'bg-white dark:bg-zinc-700 text-gray-900 dark:text-white shadow-sm' 
                : 'text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300'
            ]"
          >
            <!-- Icons -->
            <svg v-if="tab.id === 'create'" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" /></svg>
            <svg v-if="tab.id === 'documents'" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" /></svg>
            <svg v-if="tab.id === 'youtube'" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" /><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
            <svg v-if="tab.id === 'webpage'" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9" /></svg>
            
            {{ tab.name }}
          </button>
        </div>
      </div>

      <!-- Main Content (Scrollable) -->
      <div class="flex-1 overflow-y-auto px-8 pb-4">
        
        <!-- Create Tab -->
        <div v-if="activeTab === 'create'" class="h-full flex flex-col items-center justify-center text-center space-y-4">
             <div class="p-4 rounded-full bg-gray-50 dark:bg-zinc-800 text-gray-900 dark:text-white mb-2">
                 <svg class="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" /></svg>
             </div>
             <h3 class="text-lg font-medium text-gray-900 dark:text-white">Write a Memory</h3>
             <p class="text-sm text-gray-500 max-w-xs mx-auto">Create a new memory directly in the editor with full formatting support.</p>
             <button @click="navigateToEditor" class="mt-4 px-6 py-2 bg-black text-white dark:bg-white dark:text-black rounded-lg hover:opacity-80 transition-colors font-medium">
                 Open Editor
             </button>
        </div>

        <!-- Documents Tab -->
        <div v-else-if="activeTab === 'documents'" class="space-y-6">
          
          <!-- Drop Zone -->
          <div 
            @dragover.prevent="isDragging = true"
            @dragleave.prevent="isDragging = false"
            @drop.prevent="handleDrop"
            :class="[
              'border-2 border-dashed rounded-xl p-10 flex flex-col items-center justify-center transition-colors cursor-pointer min-h-[200px]',
              isDragging 
                ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/10' 
                : 'border-gray-200 dark:border-zinc-700 hover:border-gray-300 dark:hover:border-zinc-600 bg-gray-50/50 dark:bg-zinc-800/30'
            ]"
            @click="triggerFileInput"
          >
            <input type="file" ref="fileInput" @change="handleFileChange" class="hidden" />
            
            <!-- Default State -->
            <template v-if="!selectedFile && !uploadSuccess">
                <svg class="w-10 h-10 text-gray-400 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                </svg>
                <p class="text-gray-600 dark:text-gray-300 font-medium">Drag & drop files here, or click to upload</p>
                <p class="text-xs text-gray-400 mt-2">PDF, DOCX, TXT, MD (Max 10MB)</p>
            </template>

            <!-- Loading State -->
             <div v-else-if="uploading" class="flex flex-col items-center w-full max-w-xs">
                <LoadingLogo size="md" />
                <span class="text-sm text-gray-600 dark:text-gray-300 mt-3">Uploading...</span>
            </div>

            <!-- Uploaded File Item (Inside Dropzone or Replacing it?) 
                 Mockup shows file list item below dropzone if multiple, or inside? 
                 It resembles a list item. I will show it here if selected. -->
             <div v-else-if="selectedFile || uploadSuccess" class="w-full bg-gray-50 dark:bg-zinc-800/30 border border-gray-200 dark:border-zinc-700 rounded-lg p-3 flex items-center justify-between">
                <div class="flex items-center gap-3 overflow-hidden">
                    <div class="h-10 w-10 flex-shrink-0 bg-white dark:bg-zinc-800 rounded-lg flex items-center justify-center text-gray-900 dark:text-white border border-gray-100 dark:border-zinc-700">
                        <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" /></svg>
                    </div>
                    <div class="min-w-0">
                        <p class="text-sm font-medium text-gray-900 dark:text-gray-100 truncate">{{ selectedFile?.name || 'uploaded_file.pdf' }}</p>
                        <p class="text-xs text-gray-500">{{ formatSize(selectedFile?.size || 2400000) }}</p>
                    </div>
                </div>
                <div class="flex items-center gap-2">
                    <div class="p-1 text-gray-900 dark:text-white">
                         <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="3"><path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7" /></svg>
                    </div>
                    <button @click.stop="clearFile" class="text-gray-400 hover:text-red-500 p-1">
                         <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" /></svg>
                    </button>
                </div>
            </div>
          </div>

          <!-- Configuration Section -->
          <div v-if="selectedFile || uploadSuccess" class="animate-fade-in space-y-6">
              
              <!-- Ingest Mode -->
              <div>
                  <h4 class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">Ingestion Settings</h4>
                  <div class="flex gap-6">
                      <label class="flex items-center gap-2 cursor-pointer">
                          <input type="radio" name="ingest_mode" value="full" checked class="text-blue-600 focus:ring-blue-500 border-gray-300">
                          <span class="text-sm text-gray-600 dark:text-gray-400">Full document</span>
                      </label>
                      <label class="flex items-center gap-2 cursor-pointer">
                          <input type="radio" name="ingest_mode" value="selected" class="text-blue-600 focus:ring-blue-500 border-gray-300">
                          <span class="text-sm text-gray-600 dark:text-gray-400">Selected pages</span>
                      </label>
                  </div>
              </div>
          </div>

        </div>

        <!-- YouTube Tab -->
        <div v-else-if="activeTab === 'youtube'" class="h-full flex flex-col transition-all duration-300 ease-out" :class="youtubePreview.videoId ? 'justify-start pt-4' : 'justify-center'">
             <div class="w-full max-w-md mx-auto transition-all duration-300">
                 <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2 text-left">YouTube Video URL</label>
                 <div class="relative">
                     <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                         <svg class="h-5 w-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                             <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" /><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                         </svg>
                     </div>
                     <input 
                        v-model="urlInput" 
                        type="url" 
                        class="block w-full pl-10 pr-3 py-3 border border-gray-300 dark:border-zinc-700 rounded-lg focus:outline-none focus:ring-1 focus:ring-black dark:focus:ring-white dark:bg-zinc-800 dark:text-white sm:text-sm" 
                        placeholder="https://www.youtube.com/watch?v=..."
                        @keyup.enter="ingest"
                        @input="handleYouTubeUrlChange"
                     />
                 </div>
                 <p v-if="uploading" class="mt-2 text-xs text-blue-600 dark:text-blue-400 text-left font-medium animate-pulse">
                     Downloading transcript and analyzing...
                 </p>
                 <p v-else class="mt-2 text-xs text-gray-500 text-left">
                     We'll extract the transcript and add it to your brain.
                 </p>
             </div>
             
             <!-- YouTube Preview -->
             <div v-if="youtubePreview.videoId" class="w-full max-w-md mx-auto mt-6 animate-slide-up">
                 <div class="bg-gray-50 dark:bg-zinc-800 rounded-xl overflow-hidden border border-gray-200 dark:border-zinc-700">
                     <div class="relative">
                         <img 
                             :src="youtubePreview.thumbnail" 
                             :alt="youtubePreview.title || 'Video thumbnail'"
                             class="w-full h-40 object-cover"
                         />
                         <div class="absolute inset-0 bg-black/30 flex items-center justify-center">
                             <div class="w-14 h-14 rounded-full bg-red-600 flex items-center justify-center">
                                 <svg class="w-6 h-6 text-white ml-1" fill="currentColor" viewBox="0 0 24 24">
                                     <path d="M8 5v14l11-7z"/>
                                 </svg>
                             </div>
                         </div>
                     </div>
                     <div class="p-4">
                         <p class="text-sm font-medium text-gray-900 dark:text-white line-clamp-2">{{ youtubePreview.title || 'YouTube Video' }}</p>
                         <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">youtube.com</p>
                     </div>
                 </div>
             </div>
        </div>

        <!-- Webpage Tab -->
        <div v-else-if="activeTab === 'webpage'" class="h-full flex flex-col transition-all duration-300 ease-out" :class="webpagePreview.url ? 'justify-start pt-4' : 'justify-center'">
             <div class="w-full max-w-md mx-auto transition-all duration-300">
                 <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2 text-left">Page URL</label>
                 <div class="relative">
                     <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                         <svg class="h-5 w-5 text-gray-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                             <path fill-rule="evenodd" d="M12.586 4.586a2 2 0 112.828 2.828l-3 3a2 2 0 01-2.828 0 1 1 0 00-1.414 1.414 4 4 0 005.656 0l3-3a4 4 0 00-5.656-5.656l-1.5 1.5a1 1 0 101.414 1.414l1.5-1.5zm-5 5a2 2 0 012.828 0 1 1 0 101.414-1.414 4 4 0 00-5.656 0l-3 3a4 4 0 105.656 5.656l1.5-1.5a2 2 0 10-1.414-1.414l-1.5 1.5a2 2 0 11-2.828-2.828l3-3z" clip-rule="evenodd" />
                         </svg>
                     </div>
                     <input 
                        v-model="urlInput" 
                        type="url" 
                        class="block w-full pl-10 pr-3 py-3 border border-gray-300 dark:border-zinc-700 rounded-lg focus:outline-none focus:ring-1 focus:ring-black dark:focus:ring-white dark:bg-zinc-800 dark:text-white sm:text-sm" 
                        placeholder="https://example.com/article"
                        @keyup.enter="ingest"
                        @input="handleWebpageUrlChange"
                     />
                 </div>
                 <p v-if="webpagePreview.loading" class="mt-2 text-xs text-blue-600 dark:text-blue-400 text-left font-medium animate-pulse">
                     Fetching page info...
                 </p>
                 <p v-else class="mt-2 text-xs text-gray-500 text-left">
                     We'll extract the main content and add it to your brain.
                 </p>
             </div>
             
             <!-- Webpage Preview -->
             <div v-if="webpagePreview.url && !webpagePreview.loading" class="w-full max-w-md mx-auto mt-6 animate-slide-up">
                 <div class="bg-gray-50 dark:bg-zinc-800 rounded-xl overflow-hidden border border-gray-200 dark:border-zinc-700 p-4">
                     <div class="flex items-start gap-3">
                         <div class="w-10 h-10 rounded-lg bg-white dark:bg-zinc-700 border border-gray-200 dark:border-zinc-600 flex items-center justify-center shrink-0 overflow-hidden">
                             <img 
                                 v-if="webpagePreview.favicon"
                                 :src="webpagePreview.favicon" 
                                 class="w-6 h-6"
                                 @error="webpagePreview.favicon = null"
                             />
                             <svg v-else class="w-5 h-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                 <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9" />
                             </svg>
                         </div>
                         <div class="min-w-0 flex-1">
                             <p class="text-sm font-medium text-gray-900 dark:text-white truncate">{{ webpagePreview.title || webpagePreview.domain }}</p>
                             <p class="text-xs text-gray-500 dark:text-gray-400 mt-0.5">{{ webpagePreview.domain }}</p>
                         </div>
                         <div class="shrink-0">
                             <svg class="w-4 h-4 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                                 <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7" />
                             </svg>
                         </div>
                     </div>
                 </div>
             </div>
        </div>

      </div>

      <!-- Footer -->
      <div class="border-t border-gray-100 dark:border-zinc-800 px-8 py-4 flex justify-end gap-3 bg-gray-50 dark:bg-zinc-900/50">
          <button @click="close" class="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 hover:text-gray-900 border border-gray-300 dark:border-zinc-700 rounded-lg hover:bg-gray-50 dark:hover:bg-zinc-800 transition-colors">
              Cancel
          </button>
          
          <button 
            v-if="activeTab === 'documents' || activeTab === 'webpage' || activeTab === 'youtube'"
            @click="ingest" 
            :disabled="(activeTab === 'documents' ? !selectedFile : !urlInput) || uploading"
            class="px-5 py-2 text-sm font-medium bg-black text-white dark:bg-white dark:text-black hover:opacity-80 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed shadow-sm flex items-center gap-2"
          >
              <svg v-if="uploading" class="animate-spin h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              {{ uploading ? 'Processing...' : (uploadSuccess ? 'Done' : (['webpage', 'youtube'].includes(activeTab) ? 'Ingest' : 'Add Content')) }}
          </button>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import api from '../services/api';
import { useToast } from 'vue-toastification';
import LoadingLogo from '@/components/common/LoadingLogo.vue';

const props = defineProps({
  isOpen: Boolean
});

const emit = defineEmits(['close']);
const router = useRouter();
const toast = useToast();

const activeTab = ref('documents');
const isDragging = ref(false);
const fileInput = ref(null);
const selectedFile = ref(null);
const uploading = ref(false);
const uploadSuccess = ref(false);

const tabs = [
    { id: 'create', name: 'Create', icon: 'svg-plus' },
    { id: 'documents', name: 'Documents', icon: 'svg-doc' },
    { id: 'youtube', name: 'YouTube', icon: 'svg-yt' },
    { id: 'webpage', name: 'Webpage', icon: 'svg-web' },
];

const navigateToEditor = () => {
    close();
    router.push('/editor/new');
}

const close = () => {
    emit('close');
    setTimeout(reset, 300);
};

const reset = () => {
    selectedFile.value = null;
    uploadSuccess.value = false;
    urlInput.value = '';
    youtubePreview.value = { videoId: null, thumbnail: null, title: null };
    webpagePreview.value = { url: null, domain: null, favicon: null, title: null, loading: false };
    activeTab.value = 'documents';
};

const triggerFileInput = () => {
    fileInput.value.click();
};

const handleFileChange = (e) => {
    const files = e.target.files;
    if (files.length) processFile(files[0]);
};

const handleDrop = (e) => {
    isDragging.value = false;
    const files = e.dataTransfer.files;
    if (files.length) processFile(files[0]);
};

const processFile = (file) => {
    selectedFile.value = file;
    // Simulating preview text for now from file content if feasible, or just placeholder
    // In real app, we might just show file details
};

const clearFile = () => {
    selectedFile.value = null;
    uploadSuccess.value = false;
    if (fileInput.value) fileInput.value.value = '';
};

const formatSize = (bytes) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
};

const urlInput = ref('');

// Preview State
const youtubePreview = ref({
    videoId: null,
    thumbnail: null,
    title: null
});

const webpagePreview = ref({
    url: null,
    domain: null,
    favicon: null,
    title: null,
    loading: false
});

let urlDebounceTimer = null;

// Extract YouTube video ID from various URL formats
const extractYouTubeId = (url) => {
    if (!url) return null;
    const patterns = [
        /(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([a-zA-Z0-9_-]{11})/,
        /youtube\.com\/shorts\/([a-zA-Z0-9_-]{11})/
    ];
    for (const pattern of patterns) {
        const match = url.match(pattern);
        if (match) return match[1];
    }
    return null;
};

// Handle YouTube URL changes
const handleYouTubeUrlChange = () => {
    const videoId = extractYouTubeId(urlInput.value);
    if (videoId) {
        youtubePreview.value = {
            videoId: videoId,
            thumbnail: `https://img.youtube.com/vi/${videoId}/mqdefault.jpg`,
            title: null  // Title would need API call, showing thumbnail is enough
        };
    } else {
        youtubePreview.value = { videoId: null, thumbnail: null, title: null };
    }
};

// Handle Webpage URL changes with debounce
const handleWebpageUrlChange = () => {
    clearTimeout(urlDebounceTimer);
    
    const url = urlInput.value.trim();
    if (!url || !url.startsWith('http')) {
        webpagePreview.value = { url: null, domain: null, favicon: null, title: null, loading: false };
        return;
    }
    
    urlDebounceTimer = setTimeout(() => {
        try {
            const urlObj = new URL(url);
            const domain = urlObj.hostname;
            webpagePreview.value = {
                url: url,
                domain: domain,
                favicon: `https://www.google.com/s2/favicons?sz=64&domain=${domain}`,
                title: domain,  // Use domain as title since we can't fetch page title client-side
                loading: false
            };
        } catch (e) {
            webpagePreview.value = { url: null, domain: null, favicon: null, title: null, loading: false };
        }
    }, 300);
};

const ingest = async () => {
    // if (activeTab.value === 'youtube') {
    //     toast.info('Feature coming soon');
    //     return;
    // }

    uploading.value = true;

    try {
        if (activeTab.value === 'webpage') {
             if (!urlInput.value || !urlInput.value.startsWith('http')) {
                 toast.error("Please enter a valid URL");
                 uploading.value = false;
                 return;
             }
             
             await api.post('/ingest/url', { 
                 url: urlInput.value,
                 tags: ['web-import']
             });
             
             uploadSuccess.value = true;
             toast.success('Webpage queued for ingestion');
        } 
        else if (activeTab.value === 'documents') {
            if (!selectedFile.value) {
                uploading.value = false;
                return;
            }

            const formData = new FormData();
            formData.append('file', selectedFile.value);

            await api.post('/documents/upload', formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });
            
            uploadSuccess.value = true;
            toast.success('Document uploaded successfully');
        } else if (activeTab.value === 'youtube') {
             if (!urlInput.value || !urlInput.value.includes('youtube') && !urlInput.value.includes('youtu.be')) {
                 toast.error("Please enter a valid YouTube URL");
                 uploading.value = false;
                 return;
             }
             
             await api.post('/documents/upload-youtube', { 
                 url: urlInput.value
             });
             
             uploadSuccess.value = true;
             toast.success('Video transcript queued for ingestion');
        }

        // Wait a bit then close
        setTimeout(() => {
            close();
            // Refresh dashboard
            router.go(0); 
        }, 1000);

    } catch (error) {
        console.error(error);
        toast.error('Operation failed: ' + (error.response?.data?.detail || error.message));
    } finally {
        uploading.value = false;
    }
};

</script>

<style scoped>
.animate-fade-in { animation: fadeIn 0.3s ease-out; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(5px); } to { opacity: 1; transform: translateY(0); } }

.animate-slide-up { animation: slideUp 0.4s ease-out; }
@keyframes slideUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
</style>
