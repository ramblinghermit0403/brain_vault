<template>
  <div class="markdown-editor h-full flex flex-col bg-white dark:bg-gray-800">
    <div class="p-4 border-b border-gray-200 dark:border-gray-700">
      <input 
        v-model="form.title" 
        type="text" 
        placeholder="Title..." 
        class="w-full text-lg font-medium border-none focus:ring-0 bg-transparent text-gray-900 dark:text-white placeholder-gray-400"
      />
    </div>
    
    <div class="flex-1 overflow-hidden flex flex-col">
      <textarea 
        v-model="form.content"
        placeholder="Start writing your memory... (Markdown supported)"
        class="flex-1 p-4 border-none focus:ring-0 resize-none bg-white dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-400"
      ></textarea>
    </div>
    
    <div class="p-4 border-t border-gray-200 dark:border-gray-700 flex justify-between items-center">
      <div class="text-sm text-gray-500 dark:text-gray-400">
        {{ isEditing ? 'Editing' : 'New Memory' }}
      </div>
      <div class="flex space-x-2">
        <button 
          v-if="isEditing || form.title || form.content"
          @click="cancel" 
          class="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-md transition-colors"
        >
          Cancel
        </button>
        <button 
          @click="save" 
          :disabled="!form.title || !form.content || loading"
          class="px-4 py-2 text-sm font-medium text-white dark:text-black bg-black dark:bg-white hover:bg-gray-900 dark:hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed rounded-md transition-colors"
        >
          {{ loading ? 'Saving...' : 'Save Memory' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue';
import api from '../services/api';

const props = defineProps({
  document: {
    type: Object,
    default: null
  }
});

const emit = defineEmits(['saved', 'cancelled']);
import { useToast } from 'vue-toastification';
const toast = useToast();

const form = ref({
  title: '',
  content: ''
});

const isEditing = ref(false);
const loading = ref(false);

watch(() => props.document, (newDoc) => {
  if (newDoc && newDoc.doc_type === 'memory') {
    form.value = {
      title: newDoc.title,
      content: newDoc.content || ''
    };
    isEditing.value = true;
  } else {
    form.value = { title: '', content: '' };
    isEditing.value = false;
  }
}, { immediate: true });

const save = async () => {
  if (!form.value.title || !form.value.content) return;
  
  loading.value = true;
  try {
    if (isEditing.value && props.document) {
      // Update existing memory
      await api.put(`/documents/${props.document.id}`, form.value);
    } else {
      // Create new memory
      await api.post('/documents/memory', form.value);
    }
    
    emit('saved');
    form.value = { title: '', content: '' };
    isEditing.value = false;
    toast.success('Memory saved successfully');
  } catch (error) {
    console.error('Error saving memory:', error);
    toast.error('Failed to save memory: ' + (error.response?.data?.detail || error.message));
  } finally {
    loading.value = false;
  }
};

const cancel = () => {
  emit('cancelled');
  form.value = { title: '', content: '' };
  isEditing.value = false;
};
</script>

<style scoped>
textarea {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  line-height: 1.6;
}
</style>
