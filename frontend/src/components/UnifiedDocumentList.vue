<template>
  <div class="h-full flex flex-col">
    <div class="p-6 border-b border-gray-100 dark:border-gray-700 flex justify-between items-center ">
      <div>
        <h3 class="text-lg font-bold text-gray-900 dark:text-white flex items-center gap-2">
            <svg class="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" /></svg>
            Memory List
        </h3>
        <p class="text-xs text-gray-400 mt-1">Your personal knowledge base.</p>
      </div>
      <button @click="fetchDocuments" class="text-sm text-gray-500 hover:text-black dark:text-gray-400 dark:hover:text-white font-medium">
        View All
      </button>
    </div>

    <!-- Empty State -->
    <div v-if="!loading && filteredDocuments.length === 0" class="flex-1 flex flex-col items-center justify-center p-8 text-gray-400">
         <svg class="w-12 h-12 mb-3 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" /></svg>
         <p>No documents found.</p>
    </div>

    <!-- List -->
    <div v-else class="flex-1 overflow-y-auto custom-scrollbar">
       <div v-if="loading" class="p-8 flex justify-center text-gray-400">
         <LoadingLogo size="md" />
       </div>
       <ul v-else class="divide-y divide-gray-100 dark:divide-gray-700">
         <li v-for="doc in paginatedDocuments" :key="doc.id" class="hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors duration-150 group">
           <div class="px-6 py-4 flex items-center justify-between cursor-pointer" @click="editDocument(doc)">
             <div class="flex-1 min-w-0 pr-4">
                <h4 class="text-base font-medium text-gray-900 dark:text-white truncate group-hover:text-black dark:group-hover:text-white transition-colors">
                  {{ doc.title || 'Untitled Document' }}
                </h4>
               <p class="text-sm text-gray-500 dark:text-gray-400 truncate mt-0.5 line-clamp-1">
                 {{ doc.content ? doc.content.substring(0, 120) : (doc.source || 'No content preview') }}
               </p>
               <!-- Duplication Alert -->
               <div v-if="doc.tags && doc.tags.includes('similar-content')" class="mt-2 flex items-center gap-1.5 text-amber-600 dark:text-amber-400 bg-amber-50 dark:bg-amber-900/20 px-2 py-1 rounded w-fit">
                   <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" /></svg>
                   <span class="text-xs font-semibold">Potential Duplicate</span>
               </div>
             </div>
             <div class="flex items-center gap-3">
                 <!-- Type Badge (optional, visually small) -->
                <!--
                <span :class="{'bg-purple-50 text-purple-700 dark:bg-purple-900/30 dark:text-purple-300': doc.type === 'memory', 'bg-emerald-50 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-300': doc.type !== 'memory'}" class="px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wide">
                    {{ doc.type === 'memory' ? 'MEM' : 'DOC' }}
                </span>
                -->
                <button class="text-gray-300 group-hover:text-black dark:text-gray-600 dark:group-hover:text-white p-1 rounded hover:bg-gray-100 dark:hover:bg-gray-700 transition-all">
                     <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" /></svg>
                </button>
             </div>
           </div>
         </li>
       </ul>
    </div>
    
    <!-- Pagination -->
    <div v-if="filteredDocuments.length > 0" class="p-4 border-t border-gray-100 dark:border-gray-700 flex items-center justify-between bg-white dark:bg-surface">
        <span class="text-sm text-gray-500 dark:text-gray-400">
            Page {{ currentPage }} of {{ totalPages }}
        </span>
        <div class="flex gap-2">
            <button 
                @click="currentPage--" 
                :disabled="currentPage === 1"
                class="px-3 py-1 text-sm rounded bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
                Previous
            </button>
            <button 
                @click="currentPage++" 
                :disabled="currentPage === totalPages"
                class="px-3 py-1 text-sm rounded bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
                Next
            </button>
        </div>
    </div>
    
    <ConfirmationModal 
      :is-open="showModal" 
      title="Delete Item" 
      message="Are you sure you want to delete this item? This action cannot be undone."
      confirm-text="Delete"
      :loading="deleting"
      @confirm="handleDeleteConfirm"
      @cancel="handleDeleteCancel"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import api from '../services/api';
import ConfirmationModal from './ConfirmationModal.vue';
import { useToast } from 'vue-toastification';
import LoadingLogo from '@/components/common/LoadingLogo.vue';

const router = useRouter();
const toast = useToast();
const documents = ref([]);
const loading = ref(false);
const filterType = ref('all');
const currentPage = ref(1);
const itemsPerPage = 5;

// Modal state
const showModal = ref(false);
const itemToDelete = ref(null);
const deleting = ref(false);

const filteredDocuments = computed(() => {
  if (filterType.value === 'all') {
    return documents.value;
  }
  return documents.value.filter(doc => {
    if (filterType.value === 'memory') return doc.type === 'memory';
    if (filterType.value === 'file') return doc.type === 'file' || doc.type === 'document';
    return true;
  });
});

const totalPages = computed(() => {
    return Math.ceil(filteredDocuments.value.length / itemsPerPage);
});

const paginatedDocuments = computed(() => {
    const start = (currentPage.value - 1) * itemsPerPage;
    const end = start + itemsPerPage;
    return filteredDocuments.value.slice(start, end);
});

const fetchDocuments = async () => {
  loading.value = true;
  try {
    const response = await api.get('/memory/');
    documents.value = response.data;
  } catch (error) {
    console.error('Error fetching documents:', error);
    toast.error('Failed to fetch documents');
  } finally {
    loading.value = false;
  }
};

const editDocument = (doc) => {
  router.push(`/editor/${doc.id}`);
};

const confirmDelete = (id) => {
  itemToDelete.value = id;
  showModal.value = true;
};

const handleDeleteConfirm = async () => {
  if (!itemToDelete.value) return;
  deleting.value = true;
  try {
    await api.delete(`/memory/${itemToDelete.value}`);
    await fetchDocuments();
    toast.success('Item deleted successfully');
    showModal.value = false;
    itemToDelete.value = null;
  } catch (error) {
    console.error('Error deleting document:', error);
    toast.error('Failed to delete item');
  } finally {
    deleting.value = false;
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

onMounted(fetchDocuments);

defineExpose({ fetchDocuments });
</script>
