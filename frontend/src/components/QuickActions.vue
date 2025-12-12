<template>
  <div class="fixed bottom-6 right-6 z-50 flex flex-col items-end">
    <!-- Actions Menu -->
    <transition
      enter-active-class="transition duration-200 ease-out"
      enter-from-class="opacity-0 translate-y-4 scale-95"
      enter-to-class="opacity-100 translate-y-0 scale-100"
      leave-active-class="transition duration-150 ease-in"
      leave-from-class="opacity-100 translate-y-0 scale-100"
      leave-to-class="opacity-0 translate-y-4 scale-95"
    >
      <div v-if="isOpen" class="mb-4 flex flex-col items-end space-y-3">
        <button 
          v-for="action in actions" 
          :key="action.label"
          @click="handleAction(action)"
          class="flex items-center gap-3 px-4 py-2 bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-200 rounded-lg shadow-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors border border-gray-100 dark:border-gray-700 whitespace-nowrap group"
        >
          <span class="text-sm font-medium">{{ action.label }}</span>
          <div class="p-2 rounded-full text-gray-700 dark:text-gray-200">
             <component :is="action.icon" class="w-5 h-5" />
          </div>
        </button>
      </div>
    </transition>
    
    <!-- Main Toggle Button -->
    <button 
      @click="isOpen = !isOpen"
      :class="['flex items-center justify-center w-14 h-14 bg-indigo-600 hover:bg-indigo-700 text-white rounded-full shadow-xl transition-all duration-300 focus:outline-none focus:ring-4 focus:ring-indigo-300 dark:focus:ring-indigo-900', isOpen ? 'rotate-45' : '']"
    >
      <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" /></svg>
    </button>
  </div>
</template>

<script setup>
import { ref, h } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();
const isOpen = ref(false);

// Icon Components
const PlusIcon = () => h('svg', { class: 'w-5 h-5', fill: 'none', viewBox: '0 0 24 24', stroke: 'currentColor' }, [
  h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M12 4v16m8-8H4' })
]);
const InboxIcon = () => h('svg', { class: 'w-5 h-5', fill: 'none', viewBox: '0 0 24 24', stroke: 'currentColor' }, [
  h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10' })
]);
const TagIcon = () => h('svg', { class: 'w-5 h-5', fill: 'none', viewBox: '0 0 24 24', stroke: 'currentColor' }, [
  h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z' })
]);
const UploadIcon = () => h('svg', { class: 'w-5 h-5', fill: 'none', viewBox: '0 0 24 24', stroke: 'currentColor' }, [
  h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12' })
]);
const ReviewIcon = () => h('svg', { class: 'w-5 h-5', fill: 'none', viewBox: '0 0 24 24', stroke: 'currentColor' }, [
  h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253' })
]);

const emit = defineEmits(['open-review']);

const actions = [
  { 
    label: 'Daily Review', 
    icon: ReviewIcon, 
    color: 'bg-teal-500', 
    handler: () => emit('open-review')
  },
  { 
    label: 'Upload Document', 
    icon: UploadIcon, 
    color: 'bg-green-500', 
    handler: () => {
       const uploadSection = document.querySelector('h3');
       // Simple heuristic to find file upload or just use scroll 
       // Better: Just focus input? No file input depends on component.
       // Let's just create a ref in dashboard later if needed? 
       // For now scroll to top as fallback or just nothing if not found.
       // Wait, "triggerUploadFocus" in previous code was mostly placeholder.
       // Let's make it trigger the file input click if possible? 
       // Implemented: Try to find the file input from the Floating Action.
       // Actually simpler: Scroll to the dashboard grid?
       // Let's stick to router pushes for now except Upload.
       document.querySelector('input[type="file"]')?.click();
    } 
  },
  { 
    label: 'Organize Tags', 
    icon: TagIcon, 
    color: 'bg-purple-500', 
    handler: () => router.push('/settings') 
  },
  { 
    label: 'Review Inbox', 
    icon: InboxIcon, 
    color: 'bg-orange-500', 
    handler: () => router.push('/inbox') 
  },
  { 
    label: 'New Memory', 
    icon: PlusIcon, 
    color: 'bg-blue-600', 
    handler: () => router.push('/editor/new') 
  },
];

const handleAction = (action) => {
  action.handler();
  isOpen.value = false;
};
</script>
