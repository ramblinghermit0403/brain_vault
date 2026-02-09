<template>
  <div class="h-full flex flex-col">
    <!-- Header -->
    <div class="p-6 border-b border-gray-100 dark:border-gray-700 flex justify-between items-center">
      <div>
        <h3 class="text-lg font-bold text-gray-900 dark:text-white flex items-center gap-2">
            <svg class="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" /></svg>
            Recent Inbox
        </h3>
        <p class="text-xs text-gray-400 mt-1">Pending items waiting for review.</p>
      </div>
      <button 
        @click="inboxStore.fetchInbox" 
        class="text-sm text-gray-500 hover:text-black dark:text-gray-400 dark:hover:text-white font-medium flex items-center gap-1"
        :disabled="loading"
      >
        <span v-if="loading">Loading...</span>
        <span v-else>Refresh</span>
      </button>
    </div>

    <!-- Empty State -->
    <div v-if="!loading && items.length === 0" class="flex-1 flex flex-col items-center justify-center p-8 text-gray-400">
         <svg class="w-12 h-12 mb-3 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" /></svg>
         <p>No pending items.</p>
    </div>

    <!-- List -->
    <div v-else class="flex-1 overflow-y-auto custom-scrollbar">
       <ul class="divide-y divide-gray-100 dark:divide-gray-700">
         <li 
           v-for="item in paginatedItems" 
           :key="item.id" 
           class="hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors duration-150 group cursor-pointer"
           @click="viewItem(item)"
         >
           <div class="px-6 py-4 flex items-center justify-between">
             <div class="flex-1 min-w-0 pr-4">
               <div class="flex items-center gap-2 mb-1">
                 <span :class="[
                   'inline-flex items-center px-2 py-0.5 rounded text-xs font-medium',
                   item.source === 'agent_drop' 
                     ? 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400' 
                     : item.source === 'browser_extension'
                       ? 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400'
                       : 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200'
                 ]">
                   <svg v-if="item.source === 'agent_drop'" class="mr-1.5 h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                     <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                   </svg>
                   <svg v-else-if="item.source === 'browser_extension'" class="mr-1.5 h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                     <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9" />
                   </svg>
                   <svg v-else class="mr-1.5 h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                     <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                   </svg>
                   {{ formatSource(item) }}
                 </span>
                 <h4 class="text-base font-medium text-gray-900 dark:text-white truncate group-hover:text-black dark:group-hover:text-white transition-colors">{{ item.details || 'Inbox Item' }}</h4>
               </div>
               <p class="text-sm text-gray-500 dark:text-gray-400 truncate mt-0.5 line-clamp-1">{{ item.content }}</p>
             </div>
             <div class="flex items-center gap-3">
               <span class="text-xs text-gray-400 dark:text-gray-500">{{ formatDate(item.created_at) }}</span>
               <button class="text-gray-300 group-hover:text-black dark:text-gray-600 dark:group-hover:text-white p-1 rounded hover:bg-gray-100 dark:hover:bg-gray-700 transition-all">
                 <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" /></svg>
               </button>
             </div>
           </div>
         </li>
       </ul>
    </div>
    
    <!-- Pagination -->
    <div v-if="items.length > 0" class="p-4 border-t border-gray-100 dark:border-gray-700 flex items-center justify-between bg-white dark:bg-surface">
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
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useInboxStore } from '../stores/inbox';

const router = useRouter();
const inboxStore = useInboxStore();

// Ensure inbox data is loaded (DashboardView calls fetchInbox but safe to check)
// inboxStore.items is reactive

const items = computed(() => inboxStore.items);
const loading = computed(() => false); // Store typically handles loading state, assume ready or added explicitly
const currentPage = ref(1);
const itemsPerPage = 5;

const totalPages = computed(() => {
    return Math.max(1, Math.ceil(items.value.length / itemsPerPage));
});

const paginatedItems = computed(() => {
    const start = (currentPage.value - 1) * itemsPerPage;
    const end = start + itemsPerPage;
    return items.value.slice(start, end);
});

const viewItem = (item) => {
  router.push({ path: '/inbox', query: { selected: item.id } });
};

const formatDate = (dateStr) => {
  if (!dateStr) return '';
  const date = new Date(dateStr);
  // Compare to today
  const now = new Date();
  const diffMs = now - date;
  const diffMins = Math.floor(diffMs / 60000);
  
  if (diffMins < 60) return `${diffMins}m ago`;
  if (diffMins < 1440) return `${Math.floor(diffMins/60)}h ago`;
  
  return date.toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
};

const formatSource = (item) => {
  if (item.source === 'agent_drop') return 'Agent';
  if (item.source === 'browser_extension') return 'Extension';
  return 'User';
};
</script>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
  width: 4px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: rgba(156, 163, 175, 0.3);
  border-radius: 10px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: rgba(156, 163, 175, 0.5);
}
</style>
