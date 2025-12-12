<template>
  <div class="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6">
    <!-- Backdrop -->
    <div @click="close" class="absolute inset-0 bg-gray-900/50 backdrop-blur-sm transition-opacity"></div>

    <!-- Modal Card -->
    <div class="relative w-full max-w-2xl h-[650px] bg-white dark:bg-app rounded-3xl shadow-2xl overflow-hidden flex flex-col border border-gray-100 dark:border-gray-700">
        
        <!-- Header -->
        <div class="px-6 py-4 border-b border-gray-100 dark:border-gray-800 flex items-center justify-between bg-white/80 dark:bg-app/80 backdrop-blur z-10">
           <h1 class="text-xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
              <svg class="w-6 h-6 text-indigo-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" /></svg>
              Daily Review
           </h1>
           <button @click="close" class="p-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 bg-gray-100 dark:bg-gray-800 rounded-full transition-colors">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" /></svg>
           </button>
        </div>

        <!-- Content Area -->
        <div class="flex-1 overflow-y-auto overflow-x-hidden p-6 relative bg-gray-50 dark:bg-surface/50">
      <div v-if="loading" class="animate-pulse flex flex-col items-center">
         <div class="w-64 h-80 bg-gray-200 dark:bg-surface rounded-xl mb-4"></div>
         <div class="text-gray-500">Curating your review...</div>
      </div>
      
      <div v-else-if="memories.length === 0 || isCompleted" class="flex flex-col items-center justify-center h-full text-center max-w-md mx-auto">
         <div class="p-4 bg-green-100 dark:bg-green-900/30 rounded-full mb-6 text-green-600 dark:text-green-400">
            <svg class="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
         </div>
         <h2 class="text-2xl font-bold text-gray-900 dark:text-white mb-2">All Caught Up!</h2>
         <p class="text-gray-500 dark:text-text-secondary mb-8">You've reviewed all {{ memories.length }} memories for today.</p>
         <button @click="close" class="px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition">Return to Dashboard</button>
      </div>

      <div v-else class="w-full max-w-2xl mx-auto flex flex-col h-full justify-center">
         <!-- Card Stack Effect -->
         <div class="bg-white dark:bg-surface rounded-2xl shadow-sm border border-gray-200 dark:border-border overflow-hidden flex flex-col min-h-[400px]">
            <!-- Badge -->
            <div class="px-6 py-3 border-b border-gray-100 dark:border-border flex justify-between items-center bg-gray-50/50 dark:bg-white/5">
               <span 
                 class="px-2 py-1 text-xs font-medium rounded-md uppercase tracking-wide"
                 :class="currentMemory.reason === 'recent' ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400' : 'bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-400'"
               >
                 {{ currentMemory.reason === 'recent' ? 'Fresh Memory' : 'Rediscover' }}
               </span>
               <span class="text-xs font-medium text-gray-500 dark:text-gray-400">
                 {{ currentIndex + 1 }} / {{ memories.length }}
               </span>
            </div>
            
            <div class="flex-1 p-6 md:p-8 overflow-y-auto max-h-[60vh]">
               <h2 class="text-2xl font-bold text-gray-900 dark:text-white mb-4">{{ currentMemory.title }}</h2>
               <div class="prose dark:prose-invert max-w-none text-gray-700 dark:text-gray-300 whitespace-pre-wrap">
                  {{ currentMemory.content }}
               </div>
               
               <div v-if="currentMemory.tags && currentMemory.tags.length" class="mt-6 flex flex-wrap gap-2">
                 <span v-for="tag in currentMemory.tags" :key="tag" class="text-xs text-gray-500 bg-gray-100 dark:bg-gray-800 px-2 py-1 rounded">#{{ tag }}</span>
               </div>
            </div>
            
            <div class="bg-gray-50 dark:bg-gray-800/50 p-4 flex justify-between items-center border-t border-gray-100 dark:border-border">
               <button @click="prev" :disabled="currentIndex === 0" class="text-gray-500 hover:text-gray-900 dark:hover:text-white disabled:opacity-30 transition-colors">
                  Previous
               </button>
               <button @click="next" class="px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition">
                  {{ isLast ? 'Finish' : 'Next' }}
               </button>
            </div>
         </div>
      </div>
     </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
// No router needed
import api from '../services/api';

const emit = defineEmits(['close']);
const loading = ref(true);
const memories = ref([]);
const currentIndex = ref(0);
const isCompleted = ref(false);

const currentMemory = computed(() => memories.value[currentIndex.value]);
const isLast = computed(() => currentIndex.value === memories.value.length - 1);

const fetchReview = async () => {
  loading.value = true;
  try {
    const res = await api.get('/memory/review');
    memories.value = res.data;
  } catch (err) {
    console.error(err);
  } finally {
    loading.value = false;
  }
};

const next = () => {
  if (isLast.value) {
    isCompleted.value = true;
  } else {
    currentIndex.value++;
  }
};

const prev = () => {
  if (currentIndex.value > 0) {
    currentIndex.value--;
  }
};

const close = () => {
  emit('close');
};

const formatDate = (dateStr) => {
  return new Date(dateStr).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' });
};

onMounted(() => {
  fetchReview();
});
</script>
