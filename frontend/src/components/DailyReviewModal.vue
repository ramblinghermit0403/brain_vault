<template>
  <div class="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6" role="dialog" aria-modal="true">
    
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
        <h3 class="text-2xl font-bold text-gray-900 dark:text-white mb-1">Daily Review</h3>
        <p class="text-gray-500 dark:text-gray-400 text-sm">Review your memories to reinforce learning.</p>
      </div>

      <!-- Main Content -->
      <div class="flex-1 overflow-y-auto px-8 pb-4 custom-scrollbar">
        
        <!-- Loading State -->
        <div v-if="loading" class="h-full flex flex-col items-center justify-center text-center">
            <LoadingLogo size="lg" />
            <p class="text-gray-400 text-sm mt-4">Curating fresh memories...</p>
        </div>

        <!-- Completion State -->
        <div v-else-if="memories.length === 0 || isCompleted" class="h-full flex flex-col items-center justify-center text-center space-y-6">
             <div class="p-4 rounded-full bg-gray-50 dark:bg-zinc-800 text-gray-900 dark:text-white">
                 <svg class="w-12 h-12" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                 </svg>
             </div>
             <h3 class="text-xl font-bold text-gray-900 dark:text-white">All Caught Up!</h3>
             <p class="text-gray-500 dark:text-gray-400 max-w-xs mx-auto">You've reviewed all queued memories for today. Great job keeping your knowledge fresh.</p>
             <button @click="close" class="mt-2 px-6 py-2 bg-black text-white dark:bg-white dark:text-black rounded-lg hover:opacity-80 transition-colors font-medium">
                 Return to Dashboard
             </button>
        </div>

        <!-- Memory Review View -->
        <div v-else class="space-y-6">
            <!-- Progress Indicator -->
            <div class="flex items-center justify-between text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-2">
                <span>Memory {{ currentIndex + 1 }} of {{ memories.length }}</span>
                <span :class="currentMemory.reason === 'recent' ? 'text-green-600 dark:text-green-400' : 'text-blue-600 dark:text-blue-400'">
                    {{ currentMemory.reason === 'recent' ? 'Fresh' : 'Rediscovery' }}
                </span>
            </div>

            <!-- Content Card -->
            <div class="prose dark:prose-invert max-w-none">
                <h2 class="text-xl font-bold text-gray-900 dark:text-white mb-4">{{ currentMemory.title }}</h2>
                <div class="text-gray-700 dark:text-gray-300 whitespace-pre-wrap leading-relaxed">
                    {{ currentMemory.content }}
                </div>
            </div>

            <!-- Tags -->
            <div v-if="currentMemory.tags && currentMemory.tags.length" class="pt-4 border-t border-gray-100 dark:border-zinc-800 flex flex-wrap gap-2">
                 <span v-for="tag in currentMemory.tags" :key="tag" class="px-2 py-1 bg-gray-100 dark:bg-zinc-800 text-gray-600 dark:text-gray-300 text-xs rounded-md">
                   #{{ tag }}
                 </span>
            </div>
        </div>

      </div>

      <!-- Footer -->
      <div v-if="!loading && !isCompleted && memories.length > 0" class="border-t border-gray-100 dark:border-zinc-800 px-8 py-4 flex justify-between gap-3 bg-gray-50 dark:bg-zinc-900/50">
          <button 
            @click="prev" 
            :disabled="currentIndex === 0"
            class="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 hover:text-gray-900 border border-gray-300 dark:border-zinc-700 rounded-lg hover:bg-white dark:hover:bg-zinc-800 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
          >
              <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 19.5L8.25 12l7.5-7.5" />
              </svg>
              Previous
          </button>
          
          <button 
            @click="next" 
            class="px-6 py-2 text-sm font-medium bg-black text-white dark:bg-white dark:text-black hover:opacity-80 rounded-lg transition-colors shadow-sm flex items-center gap-2"
          >
              {{ isLast ? 'Finish Review' : 'Next Memory' }}
              <svg v-if="!isLast" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M8.25 4.5l7.5 7.5-7.5 7.5" />
              </svg>
              <svg v-else class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M4.5 12.75l6 6 9-13.5" />
              </svg>
          </button>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import api from '../services/api';
import LoadingLogo from '@/components/common/LoadingLogo.vue';

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
