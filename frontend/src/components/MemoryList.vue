<template>
  <div class="bg-white dark:bg-gray-800 shadow rounded-lg h-full flex flex-col">
    <div class="p-4 border-b border-gray-200 dark:border-gray-700 flex justify-between items-center">
      <h2 class="text-lg font-medium text-gray-900 dark:text-white">Your Knowledge Base</h2>
      <button @click="fetchMemories" class="text-indigo-600 dark:text-indigo-400 hover:text-indigo-800 dark:hover:text-indigo-300 text-sm font-medium">
        Refresh
      </button>
    </div>
    <div class="flex-1 overflow-y-auto p-4 space-y-4 custom-scrollbar">
      <div v-if="loading" class="text-center py-4 text-gray-500 dark:text-gray-400">Loading...</div>
      <div v-else-if="memories.length === 0" class="text-center py-4 text-gray-500 dark:text-gray-400">No memories found.</div>
      <div v-else v-for="memory in memories" :key="memory.id" class="bg-gray-50 dark:bg-gray-700/50 rounded-lg p-4 border border-gray-200 dark:border-gray-600 hover:shadow-md transition-shadow duration-200">
        <div class="flex justify-between items-start">
          <div class="flex-1">
            <div class="flex items-center space-x-2 mb-1">
              <span :class="{'bg-indigo-100 text-indigo-800 dark:bg-indigo-900 dark:text-indigo-200': memory.type === 'memory', 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900 dark:text-emerald-200': memory.type === 'document'}" class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium">
                <svg v-if="memory.type === 'memory'" class="mr-1.5 h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                </svg>
                <svg v-else class="mr-1.5 h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                {{ memory.type === 'memory' ? 'Memory' : 'File' }}
              </span>
              <h3 class="text-sm font-medium text-gray-900 dark:text-white truncate">{{ memory.title }}</h3>
            </div>
            <p class="text-sm text-gray-500 dark:text-gray-400 line-clamp-2">{{ memory.content }}</p>
            <p class="text-xs text-gray-400 dark:text-gray-500 mt-2">{{ formatDate(memory.created_at) }}</p>
          </div>
          <div class="ml-4 flex-shrink-0 flex space-x-2">
            <button v-if="memory.type === 'memory'" @click="$emit('edit', memory)" class="text-gray-400 hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors duration-200">
              <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
              </svg>
            </button>
            <button @click="confirmDelete(memory.id)" class="text-gray-400 hover:text-red-600 dark:hover:text-red-400 transition-colors duration-200">
              <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>
    <ConfirmationModal 
      :is-open="showModal" 
      title="Delete Memory" 
      message="Are you sure you want to delete this memory? This action cannot be undone."
      confirm-text="Delete"
      @confirm="handleDeleteConfirm"
      @cancel="handleDeleteCancel"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import api from '../services/api';
import ConfirmationModal from './ConfirmationModal.vue';
import { useToast } from 'vue-toastification';

const memories = ref([]);
const loading = ref(false);
const toast = useToast();

// Modal state
const showModal = ref(false);
const itemToDelete = ref(null);

const fetchMemories = async () => {
  loading.value = true;
  try {
    const response = await api.get('/memory/');
    memories.value = response.data;
  } catch (error) {
    console.error('Error fetching memories:', error);
    toast.error('Failed to fetch memories');
  } finally {
    loading.value = false;
  }
};

const confirmDelete = (id) => {
  itemToDelete.value = id;
  showModal.value = true;
};

const handleDeleteConfirm = async () => {
  if (!itemToDelete.value) return;
  
  try {
    await api.delete(`/memory/${itemToDelete.value}`);
    await fetchMemories();
    toast.success('Memory deleted successfully');
  } catch (error) {
    console.error('Error deleting memory:', error);
    toast.error('Failed to delete item');
  } finally {
    showModal.value = false;
    itemToDelete.value = null;
  }
};

const handleDeleteCancel = () => {
  showModal.value = false;
  itemToDelete.value = null;
};

const formatDate = (dateString) => {
  if (!dateString) return '';
  return new Date(dateString).toLocaleDateString() + ' ' + new Date(dateString).toLocaleTimeString();
};

onMounted(() => {
  fetchMemories();
  window.addEventListener('memory-updated', fetchMemories);
});

onUnmounted(() => {
  window.removeEventListener('memory-updated', fetchMemories);
});

defineExpose({ fetchMemories });
</script>
