<template>
  <div class="h-screen flex flex-col bg-gray-50 dark:bg-app transition-colors duration-300 font-sans overflow-hidden">
    <NavBar />

    <main class="flex-1 overflow-hidden">
       <div class="max-w-7xl mx-auto h-full flex pt-6 pb-6 px-4 sm:px-6 lg:px-8 gap-6">
           
           <!-- Left Pane: Incoming Items -->
           <div class="w-1/3 flex flex-col bg-white dark:bg-surface rounded-xl shadow-sm border border-gray-200 dark:border-border overflow-hidden">
               <div class="p-4 border-b border-gray-200 dark:border-border flex justify-between items-center bg-gray-50/50 dark:bg-surface-2">
                   <h2 class="text-base font-semibold text-gray-900 dark:text-text-primary">Incoming Items</h2>
                   <div class="flex gap-2 text-gray-400">
                       <svg class="w-4 h-4 cursor-pointer hover:text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4h13M3 8h9m-9 4h6m4 0l4-4m0 0l4 4m-4-4v12" /></svg>
                   </div>
               </div>
               
               <div class="flex-1 overflow-y-auto p-3 space-y-3 custom-scrollbar">
                   <div v-if="store.items.length === 0" class="text-center py-10 text-gray-400 text-sm">
                       No pending items.
                   </div>
                   
                   <div 
                     v-for="item in store.items" 
                     :key="item.id"
                     @click="selectItem(item)"
                     :class="['p-4 rounded-lg border cursor-pointer transition-all hover:shadow-sm', 
                              selectedItem?.id === item.id 
                                ? 'bg-blue-50 border-blue-200 dark:bg-blue-900/20 dark:border-blue-800' 
                                : 'bg-white border-gray-200 dark:bg-surface-2 dark:border-border hover:border-blue-300 dark:hover:border-blue-700']"
                   >
                       <h3 class="font-medium text-gray-900 dark:text-text-primary mb-1 line-clamp-2">{{ item.details }}</h3>
                       <div class="flex justify-between items-end mt-2">
                           <div class="flex flex-col gap-1">
                               <span class="text-xs text-gray-500 dark:text-text-secondary">{{ item.source || 'Unknown Source' }}</span>
                               <span :class="['inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-medium w-fit', item.status === 'approved' ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' : 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200']">
                                   {{ item.status === 'approved' ? 'Approved' : 'Pending' }}
                               </span>
                           </div>
                           <span class="text-[10px] text-gray-400">{{ formatTimeAgo(item.created_at) }}</span>
                       </div>
                   </div>
               </div>
           </div>

           <!-- Right Pane: Detail View -->
           <div class="w-2/3 bg-white dark:bg-surface rounded-xl shadow-sm border border-gray-200 dark:border-border flex flex-col overflow-hidden">
               <div v-if="selectedItem" class="flex flex-col h-full">
                   <!-- Content Header -->
                   <div class="p-6 border-b border-gray-200 dark:border-border">
                       <div class="flex flex-col gap-2 mb-4">
                           <div class="flex justify-between items-start">
                               <h1 class="text-2xl font-bold text-gray-900 dark:text-text-primary leading-tight">{{ selectedItem.details }}</h1>
                               <span :class="['inline-flex items-center px-2 py-1 rounded text-xs font-medium shrink-0', selectedItem.status === 'approved' ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' : 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200']">
                                   {{ selectedItem.status === 'approved' ? 'Approved' : 'Pending' }}
                               </span>
                           </div>
                           
                           <!-- Similarity Alert -->
                           <div v-if="similarityData && similarityData.score > 0" class="flex items-center gap-2 p-3 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-md text-sm text-yellow-800 dark:text-yellow-200">
                               <svg class="w-5 h-5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" /></svg>
                               <span>
                                   Matches existing content: <span class="font-bold border-b border-yellow-600/30 cursor-pointer" @click="router.push(`/editor/${similarityData.type === 'memory' ? 'mem_' : 'doc_'}${similarityData.source_id}`)">{{ similarityData.source_title }}</span> ({{ similarityData.score }}%)
                               </span>
                           </div>
                           
                           <!-- Tags -->
                           <div class="flex flex-wrap items-center gap-2 mt-2">
                               <div v-if="selectedItem.tags && selectedItem.tags.length" class="flex flex-wrap gap-2">
                                   <span v-for="tag in selectedItem.tags" :key="tag" :class="['text-xs px-2 py-0.5 rounded-full border flex items-center gap-1 group', tag === 'similar-content' ? 'hidden' : 'bg-gray-100 text-gray-600 border-gray-200 dark:bg-gray-700 dark:text-gray-300 dark:border-gray-600']">
                                       #{{ tag }}
                                       <button @click.stop="removeTag(tag)" class="opacity-0 group-hover:opacity-100 text-gray-400 hover:text-red-500 transition-opacity focus:outline-none" title="Remove tag">
                                           <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" /></svg>
                                       </button>
                                   </span>
                               </div>

                               <!-- Add Tag Input -->
                               <div class="relative flex items-center">
                                   <input 
                                     v-model="newTagInput"
                                     @keydown.enter="addNewTag"
                                     placeholder="+ Add tag" 
                                     class="text-xs px-2 py-1 rounded-full border border-gray-200 dark:border-gray-600 bg-transparent text-gray-600 dark:text-gray-300 focus:outline-none focus:border-blue-400 focus:ring-1 focus:ring-blue-400 w-24 transition-all"
                                   />
                               </div>
                           </div>
                       </div>

                       <div class="flex items-center gap-6 text-sm text-gray-500 dark:text-text-secondary">
                           <div class="flex flex-col">
                               <span class="text-xs font-medium text-gray-400 uppercase tracking-wider">Source</span>
                               <span>{{ selectedItem.source || 'Direct Entry' }}</span>
                           </div>
                           <div class="flex flex-col">
                               <span class="text-xs font-medium text-gray-400 uppercase tracking-wider">Received</span>
                               <span>{{ new Date(selectedItem.created_at).toLocaleString() }}</span>
                           </div>
                       </div>
                   </div>

                   <!-- Content Body -->
                   <div class="flex-1 overflow-y-auto p-6 custom-scrollbar">
                       <div class="prose dark:prose-invert max-w-none">
                           <p class="whitespace-pre-wrap text-gray-700 dark:text-gray-300">{{ selectedItem.content }}</p>
                       </div>
                   </div>

                   <!-- Action Footer -->
                   <div class="p-4 border-t border-gray-200 dark:border-border bg-gray-50 dark:bg-surface-2 flex justify-end gap-3 shrink-0">
                       <button 
                         @click="startEditing(selectedItem)"
                         class="px-4 py-2 bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-200 text-sm font-medium rounded-lg border border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500 shadow-sm flex items-center gap-2"
                       >
                         <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" /></svg>
                         Edit Full Content
                       </button>
                       <button 
                         @click="dismissItem(selectedItem)"
                         class="px-4 py-2 bg-white dark:bg-gray-700 text-red-600 dark:text-red-400 text-sm font-medium rounded-lg border border-gray-300 dark:border-gray-600 hover:bg-red-50 dark:hover:bg-red-900/20 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 shadow-sm flex items-center gap-2"
                       >
                         <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" /></svg>
                         Dismiss
                       </button>
                       <button 
                         @click="approveItem(selectedItem)"
                         :disabled="selectedItem.status === 'approved'"
                         :class="['px-4 py-2 text-white text-sm font-medium rounded-lg shadow-sm flex items-center gap-2 min-w-[100px] justify-center', selectedItem.status === 'approved' ? 'bg-green-600 cursor-default' : 'bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500']"
                       >
                         {{ selectedItem.status === 'approved' ? 'Approved' : 'Approve' }}
                       </button>
                   </div>
               </div>

               <!-- Empty Selection State -->
               <div v-else class="h-full flex flex-col items-center justify-center text-gray-400">
                   <div class="p-4 bg-gray-50 dark:bg-surface-2 rounded-full mb-4">
                       <svg class="w-12 h-12 text-gray-300 dark:text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" /></svg>
                   </div>
                   <h3 class="text-lg font-medium text-gray-900 dark:text-text-primary">Select an item to review</h3>
                   <p class="mt-1">Choose a pending memory from the list to view details and take action.</p>
               </div>
           </div>
       </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';
import { useInboxStore } from '../stores/inbox';
import { useRouter } from 'vue-router';
import api from '../services/api';
import NavBar from '../components/NavBar.vue';
import { useToast } from 'vue-toastification';

const store = useInboxStore();
const router = useRouter();
const toast = useToast();
const selectedItem = ref(null);
// Script addition for similarityData
const similarityData = ref(null);
const newTagInput = ref('');

const addNewTag = async () => {
    if (!newTagInput.value.trim() || !selectedItem.value) return;
    
    const tagToAdd = newTagInput.value.trim().toLowerCase().replace(/[^a-z0-9-_]/g, ''); // Basic sanitization
    if (!tagToAdd) return;

    if (selectedItem.value.tags && selectedItem.value.tags.includes(tagToAdd)) {
        newTagInput.value = '';
        return;
    }

    try {
        const currentTags = selectedItem.value.tags || [];
        const newTags = [...currentTags, tagToAdd];
        
        // Optimistic update
        selectedItem.value.tags = newTags;
        newTagInput.value = '';
        
        await api.put(`/inbox/${selectedItem.value.id}`, {
            content: selectedItem.value.content,
            title: selectedItem.value.details,
            tags: newTags
        });
        toast.success(`Tag added`);
    } catch (e) {
        toast.error('Failed to add tag');
    }
};

watch(() => selectedItem.value, (newItem) => {
    if (newItem && newItem.task_type) {
        try {
            similarityData.value = JSON.parse(newItem.task_type);
        } catch (e) {
            similarityData.value = null;
        }
    } else {
        similarityData.value = null;
    }
});

onMounted(async () => {
  await store.fetchInbox();
  store.connectWebSocket();
  if (store.items.length > 0 && !selectedItem.value) {
      selectedItem.value = store.items[0];
  }
});

watch(() => store.items, (newItems) => {
    if (newItems.length > 0 && !selectedItem.value) {
        selectedItem.value = newItems[0];
    } else if (selectedItem.value) {
        // Check if selected item still exists in new list
        const found = newItems.find(i => i.id === selectedItem.value.id);
        if (found) {
            // Update reference to get new data (e.g. tags)
            selectedItem.value = found;
        } else {
            // Item removed? Select first or null
            selectedItem.value = newItems.length > 0 ? newItems[0] : null;
        }
    }
});

const selectItem = (item) => {
    selectedItem.value = item;
};

const formatTimeAgo = (dateString) => {
    if (!dateString) return '';
    const date = new Date(dateString);
    const now = new Date();
    const diff = (now - date) / 1000;
    if (diff < 60) return 'Just now';
    if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
    if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
    return `${Math.floor(diff / 86400)}d ago`;
};

const startEditing = (item) => {
    router.push(`/editor/${item.id}`);
};

const dismissItem = async (item) => {
    if (confirm('Dismiss this item from inbox?')) {
        try {
            await store.handleAction(item.id, 'dismiss');
            toast.success('Item dismissed');
            if (selectedItem.value?.id === item.id) {
                selectedItem.value = store.items.length > 0 ? store.items[0] : null;
            }
        } catch (e) {
            toast.error('Failed to dismiss item');
        }
    }
};

const removeTag = async (tagToRemove) => {
    if (!selectedItem.value) return;
    try {
        const newTags = selectedItem.value.tags.filter(t => t !== tagToRemove);
        // Optimistic update
        selectedItem.value.tags = newTags;
        
        await api.put(`/inbox/${selectedItem.value.id}`, {
            content: selectedItem.value.content,
            title: selectedItem.value.details,
            tags: newTags
        });
        toast.success(`Tag #${tagToRemove} removed`);
    } catch (e) {
        toast.error('Failed to remove tag');
    }
};

const approveItem = async (item) => {
    try {
        await store.handleAction(item.id, 'approve');
        toast.success('Item approved and moved to memory');
        if (selectedItem.value?.id === item.id) {
            selectedItem.value = store.items.length > 0 ? store.items[0] : null;
        }
    } catch (e) {
        toast.error('Failed to approve item');
    }
};
</script>
