<template>
  <div class="w-full">
      <div 
        @dragover.prevent="isDragging = true" 
        @dragleave.prevent="isDragging = false" 
        @drop.prevent="handleDrop"
        :class="['relative border-2 border-dashed rounded-xl p-4 text-center transition-all duration-200 ease-in-out cursor-pointer group', 
                 isDragging ? 'border-indigo-500 bg-indigo-50 dark:bg-indigo-900/20' : 'border-gray-200 dark:border-gray-700 hover:border-indigo-400 hover:bg-gray-50 dark:hover:bg-gray-700/50']"
      >
          <input type="file" ref="fileInput" @change="handleFileChange" class="hidden" />
          
          <div v-if="!selectedFile && !uploading && !success" @click="$refs.fileInput.click()" class="flex flex-col items-center py-2">
               <svg class="w-8 h-8 text-indigo-400 mb-2 group-hover:scale-110 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" /></svg>
               <span class="text-sm font-medium text-gray-600 dark:text-gray-300">Click to upload or drag & drop</span>
               <span class="text-xs text-gray-400 mt-1">PDF, TXT, MD, DOCX</span>
          </div>

          <!-- Selected File State -->
          <div v-else-if="selectedFile && !uploading && !success" class="flex items-center justify-between p-2">
               <div class="flex items-center gap-3 overflow-hidden">
                   <div class="h-8 w-8 rounded bg-indigo-100 dark:bg-indigo-900/50 text-indigo-600 flex items-center justify-center shrink-0">
                       <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" /></svg>
                   </div>
                   <span class="text-sm font-medium text-gray-900 dark:text-white truncate">{{ selectedFile.name }}</span>
               </div>
               <button @click.stop="uploadFile" class="px-3 py-1.5 bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-bold rounded-md transition-colors shadow-sm">
                   Upload
               </button>
          </div>

           <!-- Uploading State -->
          <div v-else-if="uploading" class="flex flex-col items-center py-2">
               <div class="w-full bg-gray-200 rounded-full h-1.5 dark:bg-gray-700 mb-3 mx-4">
                  <div class="bg-indigo-600 h-1.5 rounded-full animate-pulse w-2/3 mx-auto"></div>
                </div>
               <span class="text-xs text-indigo-600 dark:text-indigo-400 font-medium">Uploading...</span>
          </div>

           <!-- Success State -->
           <div v-else-if="success" class="flex flex-col items-center py-2 animate-fade-in">
               <svg class="w-8 h-8 text-green-500 mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" /></svg>
               <span class="text-sm font-medium text-green-600 dark:text-green-400">Upload Complete!</span>
               <button @click="reset" class="text-xs text-gray-400 hover:text-gray-600 underline mt-1">Upload another</button>
           </div>
           
           <!-- Error Message -->
           <div v-if="message && !success && !uploading" class="absolute inset-x-0 bottom-0 p-2 bg-red-100 dark:bg-red-900/30 text-red-600 text-xs rounded-b-xl">
               {{ message }}
           </div>
      </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import api from '../services/api';

const selectedFile = ref(null);
const uploading = ref(false);
const message = ref('');
const success = ref(false);
const isDragging = ref(false);
const fileInput = ref(null);

const handleDrop = (e) => {
    isDragging.value = false;
    const files = e.dataTransfer.files;
    if (files.length) {
        selectedFile.value = files[0];
        message.value = '';
    }
};

const handleFileChange = (event) => {
  selectedFile.value = event.target.files[0];
  message.value = '';
};

const uploadFile = async () => {
    if (!selectedFile.value) return;

  uploading.value = true;
  const formData = new FormData();
  formData.append('file', selectedFile.value);

  try {
    await api.post('/documents/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    success.value = true;
    message.value = '';
    selectedFile.value = null; // Clear immediately to show success state
    
    // Auto reset after 3s
    setTimeout(() => {
        if (success.value) reset();
    }, 3000);

  } catch (error) {
    message.value = 'Failed: ' + (error.response?.data?.detail || error.message);
    success.value = false;
    // Keep selected file so user can retry
  } finally {
    uploading.value = false;
  }
};

const reset = () => {
    success.value = false;
    message.value = '';
    selectedFile.value = null;
    if(fileInput.value) fileInput.value.value = '';
}
</script>

<style scoped>
.animate-fade-in { animation: fadeIn 0.3s ease-out; }
@keyframes fadeIn { from { opacity: 0; transform: scale(0.95); } to { opacity: 1; transform: scale(1); } }
</style>
