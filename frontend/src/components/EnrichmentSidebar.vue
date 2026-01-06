<template>
  <div class="h-full flex flex-col bg-white dark:bg-surface border-r border-gray-200 dark:border-border">
    <!-- Header -->
    <div class="p-4 border-b border-gray-200 dark:border-border flex items-center justify-between">
      <h2 class="text-sm font-semibold text-gray-900 dark:text-gray-100">Intelligence</h2>
      <div v-if="loading" class="animate-spin h-4 w-4 border-2 border-primary-500 border-t-transparent rounded-full font-sans"></div>
    </div>

    <!-- Content -->
    <div class="flex-1 overflow-y-auto p-4 space-y-6">
      
      <!-- No Selection State -->
      <div v-if="!activeChunk && !loading" class="text-center py-8 text-gray-500 dark:text-gray-400 text-sm">
        <p>Select a section of the document to see AI insights.</p>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="space-y-4">
        <div class="h-20 bg-gray-100 dark:bg-surface-2 rounded animate-pulse"></div>
        <div class="h-10 bg-gray-100 dark:bg-surface-2 rounded animate-pulse"></div>
        <div class="h-10 bg-gray-100 dark:bg-surface-2 rounded animate-pulse"></div>
      </div>

      <!-- Active Content -->
      <div v-if="activeChunk && !loading">
        
        <!-- Summary Section -->
        <section v-if="activeChunk.summary">
          <h3 class="text-xs uppercase tracking-wider text-gray-500 dark:text-gray-400 font-medium mb-2">Summary</h3>
          <div class="p-3 bg-gray-50 dark:bg-surface-2 rounded-lg text-sm text-gray-700 dark:text-gray-200 leading-relaxed border border-gray-100 dark:border-border">
            {{ activeChunk.summary }}
          </div>
        </section>

        <!-- Q&A Section -->
        <section v-if="activeChunk.generated_qas && activeChunk.generated_qas.length">
          <h3 class="text-xs uppercase tracking-wider text-gray-500 dark:text-gray-400 font-medium mb-2 mt-6">Suggested Questions</h3>
          <div class="space-y-3">
            <div 
              v-for="(qa, idx) in normalizedQAs" 
              :key="idx" 
              class="p-3 bg-white dark:bg-surface border border-gray-200 dark:border-border rounded-lg shadow-sm hover:shadow-md transition-shadow duration-200"
            >
              <p class="text-sm font-medium text-gray-900 dark:text-gray-100 mb-1 q-icon">{{ qa.question }}</p>
              <p class="text-xs text-gray-600 dark:text-gray-400 pl-4 border-l-2 border-primary-100 dark:border-primary-600/30">{{ qa.answer }}</p>
            </div>
          </div>
        </section>

        <!-- Entities Section -->
        <section v-if="activeChunk.entities && activeChunk.entities.length">
           <h3 class="text-xs uppercase tracking-wider text-gray-500 dark:text-gray-400 font-medium mb-2 mt-6">Entities</h3>
           <div class="flex flex-wrap gap-2">
             <span v-for="entity in activeChunk.entities" :key="entity" class="px-2 py-1 bg-blue-50 dark:bg-blue-900/30 text-blue-700 dark:text-blue-200 text-xs rounded-full border border-blue-100 dark:border-blue-900/50">
               {{ entity }}
             </span>
           </div>
        </section>

      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  activeChunk: {
    type: Object,
    default: null
  },
  loading: {
    type: Boolean,
    default: false
  }
});

// Helper to normalize QA format (handle string vs object)
const normalizedQAs = computed(() => {
  if (!props.activeChunk || !props.activeChunk.generated_qas) return [];
  
  return props.activeChunk.generated_qas.map(qa => {
    if (typeof qa === 'string') {
      // Try to parse "Q: ... A: ..." format if simple string
      if (qa.includes('Q:') && qa.includes('A:')) {
         const parts = qa.split('A:');
         return {
           question: parts[0].replace('Q:', '').trim(),
           answer: parts[1].trim()
         };
      }
      return { question: qa, answer: '' };
    }
    // Handle object format with short keys (from LLM service)
    if (qa.q && qa.a) {
        return { question: qa.q, answer: qa.a };
    }
    return qa;
  });
});
</script>

<style scoped>
.q-icon::before {
  content: "Q.";
  margin-right: 4px;
  color: #a3a3a3;
  font-size: 10px;
}
</style>
