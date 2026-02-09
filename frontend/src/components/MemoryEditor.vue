<template>
  <div class="bg-white dark:bg-surface shadow rounded-lg p-6 h-full flex flex-col">
    <!-- Header -->
    <div class="flex justify-between items-center mb-4">
        <h2 class="text-lg font-medium text-gray-900 dark:text-white">
            {{ isViewMode ? 'View Memory' : (isEditing ? 'Edit Memory' : 'Create New Memory') }}
        </h2>
        
        <!-- View Mode Actions -->
        <div v-if="isViewMode" class="flex gap-2">
            <button @click="isViewMode = false" class="text-sm px-3 py-1.5 bg-black dark:bg-white text-white dark:text-black rounded-md hover:bg-gray-900 dark:hover:bg-gray-200 transition-colors font-medium shadow-sm">
                Edit
            </button>
        </div>
    </div>
    
    <!-- View Mode -->
    <div v-if="isViewMode" class="flex-1 flex flex-col min-h-0 overflow-hidden space-y-4">
        <div>
            <h3 class="text-xl font-bold text-gray-900 dark:text-white">{{ form.title || 'Untitled' }}</h3>
        </div>
        
        <div class="flex-1 overflow-y-auto custom-scrollbar prose dark:prose-invert max-w-none pr-2">
            <div class="whitespace-pre-wrap text-gray-700 dark:text-gray-300">{{ form.content }}</div>
        </div>

        <div v-if="form.tags" class="pt-4 border-t border-gray-100 dark:border-gray-700 shrink-0">
            <div class="flex flex-wrap gap-2">
                <span v-for="tag in form.tags.split(',').filter(t=>t.trim())" :key="tag" class="px-2 py-1 bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 text-xs rounded-full">
                    #{{ tag.trim() }}
                </span>
            </div>
        </div>
    </div>
    
    <!-- Edit Mode -->
    <form v-else @submit.prevent="saveMemory" class="flex-1 flex flex-col min-h-0 space-y-4 overflow-hidden">
      <div>
        <label for="title" class="block text-sm font-medium text-gray-700 dark:text-gray-300">Title</label>
        <input type="text" id="title" v-model="form.title" required class="mt-1 block w-full border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:ring-black dark:focus:ring-white focus:border-black dark:focus:border-white sm:text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-white" placeholder="Memory Title" />
      </div>
      
      <div class="flex-1 flex flex-col min-h-0">
        <label for="content" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Content</label>
        <textarea id="content" v-model="form.content" required class="flex-1 block w-full border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:ring-black dark:focus:ring-white focus:border-black dark:focus:border-white sm:text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-white resize-none p-4" placeholder="Write your memory here..."></textarea>
      </div>

      <div>
        <label for="tags" class="block text-sm font-medium text-gray-700 dark:text-gray-300">Tags (comma separated)</label>
        <input type="text" id="tags" v-model="form.tags" class="mt-1 block w-full border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:ring-black dark:focus:ring-white focus:border-black dark:focus:border-white sm:text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-white" placeholder="AI, Project, Important" />
      </div>
      
      <div class="flex justify-end space-x-3 pt-4 border-t border-gray-100 dark:border-gray-700 shrink-0">
        <button type="button" @click="cancel" class="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">
          {{ isEditing && !isViewMode ? 'Cancel Edit' : 'Cancel' }}
        </button>
        <button type="submit" :disabled="loading" class="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white dark:text-black bg-black dark:bg-white hover:bg-gray-900 dark:hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-black dark:focus:ring-white disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2">
          <LoadingLogo v-if="loading" size="sm" class="w-4 h-4" />
          {{ loading ? 'Saving...' : 'Save Memory' }}
        </button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue';
import api from '../services/api';
import LoadingLogo from '@/components/common/LoadingLogo.vue';

const props = defineProps({
  memory: {
    type: Object,
    default: null
  }
});

const emit = defineEmits(['saved', 'cancelled']);
import { useToast } from 'vue-toastification';
const toast = useToast();

const form = ref({
  title: '',
  content: '',
  tags: ''
});

const isEditing = ref(false);
const isViewMode = ref(false); // Controls View vs Edit
const loading = ref(false);

watch(() => props.memory, (newVal) => {
  if (newVal) {
    form.value = { 
      ...newVal, 
      tags: Array.isArray(newVal.tags) ? newVal.tags.join(', ') : (newVal.tags || '') 
    };
    isEditing.value = true;
    isViewMode.value = true; // Default to view mode for existing items
  } else {
    form.value = { title: '', content: '', tags: '' };
    isEditing.value = false;
    isViewMode.value = false;
  }
}, { immediate: true });

const saveMemory = async () => {
  loading.value = true;
  try {
    const payload = {
      ...form.value,
      tags: form.value.tags.split(',').map(t => t.trim()).filter(t => t)
    };
    
    // Optimistic update if viewing
    const updatedMemory = { ...payload, id: props.memory?.id };

    if (isEditing.value) {
      await api.put(`/memory/${props.memory.id}`, payload);
      // Stay in component but switch to view
      isViewMode.value = true;
    } else {
      await api.post('/memory/', payload);
      emit('saved'); // New memory -> likely clear or close
      // Or stay? For now standard flow.
      form.value = { title: '', content: '' };
      isEditing.value = false;
    }
    
    toast.success('Memory saved successfully');
  } catch (error) {
    console.error('Error saving memory:', error);
    toast.error('Failed to save memory');
  } finally {
    loading.value = false;
  }
};

const cancel = () => {
  if (isEditing.value) {
      // If we were editing an existing item, revert logic or just go back to view
      // Ideally revert form data
      if (props.memory) {
          form.value = { 
            ...props.memory, 
            tags: Array.isArray(props.memory.tags) ? props.memory.tags.join(', ') : (props.memory.tags || '') 
          };
          isViewMode.value = true;
      } else {
          emit('cancelled'); // Fallback if somehow editing but no memory prop?
      }
  } else {
      emit('cancelled'); // Cancel creation
  }
};
</script>
