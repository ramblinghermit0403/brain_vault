<template>
  <div class="h-full flex flex-col bg-white dark:bg-surface border-r border-gray-200 dark:border-border">
    <!-- Content (Scrollable) -->
    <div class="flex-1 overflow-y-auto p-8 space-y-8 custom-scrollbar">
      
      <!-- Header Section inside scrollable area to match Properties -->
      <div class="flex items-center justify-between border-b border-gray-100 dark:border-gray-800 mb-6 pb-2">
         <h4 class="text-[11px] font-bold text-gray-900 dark:text-gray-100 uppercase tracking-wider">Intelligence</h4>
         <LoadingLogo v-if="loading" size="sm" />
      </div>

      <!-- Loading State (Center) -->
      <div v-if="loading" class="flex flex-col items-center justify-center py-8">
        <LoadingLogo size="md" />
        <span class="text-xs text-gray-400 mt-2">Analyzing content...</span>
      </div>

      <!-- No Selection State -->
      <div v-if="!activeChunk && !loading" class="text-center py-8 text-gray-500 dark:text-gray-400 text-sm">
        <p>Select a section of the document to see AI insights.</p>
      </div>

      <!-- Active Content -->
      <div v-if="activeChunk && !loading" class="space-y-8">
        
        <!-- Summary Section -->
        <section v-if="activeChunk.summary">
          <h3 class="text-xs uppercase tracking-wider text-gray-500 dark:text-gray-400 font-medium mb-3">Summary</h3>
          <div class="p-4 bg-gray-50 dark:bg-surface-2 rounded-lg text-sm text-gray-700 dark:text-gray-200 leading-relaxed border border-gray-100 dark:border-border">
            {{ activeChunk.summary }}
          </div>
        </section>

        <!-- Q&A Section -->
        <section v-if="activeChunk.generated_qas && activeChunk.generated_qas.length">
          <h3 class="text-xs uppercase tracking-wider text-gray-500 dark:text-gray-400 font-medium mb-3">Suggested Questions</h3>
          <div class="space-y-3">
            <div 
              v-for="(qa, idx) in normalizedQAs" 
              :key="idx" 
              class="p-4 bg-white dark:bg-surface border border-gray-200 dark:border-border rounded-lg shadow-sm hover:shadow-md transition-shadow duration-200"
            >
              <p class="text-sm font-medium text-gray-900 dark:text-gray-100 mb-2 q-icon">{{ qa.question }}</p>
              <p class="text-xs text-gray-600 dark:text-gray-400 pl-4 border-l-2 border-primary-100 dark:border-primary-600/30 leading-relaxed">{{ qa.answer }}</p>
            </div>
          </div>
        </section>

        <!-- Entities Section -->
        <section v-if="activeChunk.entities && activeChunk.entities.length">
           <h3 class="text-xs uppercase tracking-wider text-gray-500 dark:text-gray-400 font-medium mb-3">Entities</h3>
           <div class="flex flex-wrap gap-2">
             <span v-for="entity in activeChunk.entities" :key="entity" class="px-2.5 py-1 bg-blue-50 dark:bg-blue-900/30 text-blue-700 dark:text-blue-200 text-xs rounded-full border border-blue-100 dark:border-blue-900/50 font-medium">
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
import LoadingLogo from '@/components/common/LoadingLogo.vue';

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
