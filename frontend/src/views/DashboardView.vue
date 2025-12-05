<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900 transition-colors duration-300">
    <nav class="bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between h-16">
          <div class="flex">
            <div class="flex-shrink-0 flex items-center">
              <h1 id="tour-welcome" class="text-xl font-bold text-indigo-600 dark:text-indigo-400">Brain Vault</h1>
            </div>
          </div>
          <div class="flex items-center space-x-4">
            <ThemeToggle />
            <router-link id="tour-settings" to="/settings" class="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 px-3 py-2 rounded-md text-sm font-medium">
              Settings
            </router-link>
            <router-link id="tour-memory-map" to="/map" class="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 px-3 py-2 rounded-md text-sm font-medium">
              Memory Map
            </router-link>
            <button @click="logout" class="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 px-3 py-2 rounded-md text-sm font-medium">
              Logout
            </button>
          </div>
        </div>
      </div>
    </nav>

    <main class="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
      <div class="px-4 py-6 sm:px-0">
        <GridLayout
          v-model:layout="layout"
          :col-num="12"
          :row-height="30"
          :is-draggable="true"
          :is-resizable="true"
          :vertical-compact="true"
          :use-css-transforms="true"
        >
          <GridItem
            v-for="item in layout"
            :key="item.i"
            :x="item.x"
            :y="item.y"
            :w="item.w"
            :h="item.h"
            :i="item.i"
            :id="item.id"
            class="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden flex flex-col"
          >
            <!-- Drag Handle -->
            <div class="bg-gray-100 dark:bg-gray-700 px-4 py-2 cursor-move flex justify-between items-center border-b border-gray-200 dark:border-gray-600 shrink-0">
              <h2 class="text-sm font-medium text-gray-700 dark:text-gray-200">{{ item.title }}</h2>
              <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 8h16M4 16h16" />
              </svg>
            </div>
            
            <!-- Content -->
            <div class="flex-1 overflow-auto p-4 relative">
              <component 
                :is="item.component" 
                v-bind="getComponentProps(item.i)"
                @edit="handleEdit"
                @saved="handleSaved"
                @cancelled="handleCancelled"
                ref="componentRefs"
              />
            </div>
          </GridItem>
        </GridLayout>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, shallowRef, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { GridLayout, GridItem } from 'grid-layout-plus';
import UnifiedDocumentList from '../components/UnifiedDocumentList.vue';
import QuickActions from '../components/QuickActions.vue';
import FileUpload from '../components/FileUpload.vue';
import RetrievalTest from '../components/RetrievalTest.vue';
import ThemeToggle from '../components/ThemeToggle.vue';
import { createTour } from '../tour';

const router = useRouter();

const layout = ref([
  { x: 0, y: 0, w: 4, h: 20, i: 'documents', title: 'Knowledge Base', component: shallowRef(UnifiedDocumentList), id: 'tour-knowledge-base' },
  { x: 4, y: 0, w: 4, h: 20, i: 'actions', title: 'Quick Actions', component: shallowRef(QuickActions), id: 'tour-quick-actions' },
  { x: 8, y: 0, w: 4, h: 8, i: 'upload', title: 'Upload File', component: shallowRef(FileUpload), id: 'tour-upload' },
  { x: 8, y: 8, w: 4, h: 12, i: 'retrieval', title: 'Ask Your Brain Vault', component: shallowRef(RetrievalTest), id: 'tour-retrieval' },
]);

const getComponentProps = (id) => {
  return {};
};

const handleEdit = (document) => {
  // Navigation handled by component
};

const handleSaved = () => {
  refreshDocumentList();
};

const handleCancelled = () => {
  // No-op
};

const refreshDocumentList = () => {
  // Refresh logic if needed, but UnifiedDocumentList handles its own refresh
};

const logout = () => {
  localStorage.removeItem('token');
  router.push('/login');
};

onMounted(() => {
  const tourCompleted = localStorage.getItem('tour_completed');
  if (!tourCompleted) {
    const driver = createTour();
    driver.drive();
    localStorage.setItem('tour_completed', 'true');
  }
});
</script>

<style scoped>
:deep(.vgl-item--placeholder) {
  background: rgba(79, 70, 229, 0.2) !important;
  border-radius: 0.5rem;
  z-index: 10;
}

/* Ensure grid items have a background and shadow */
:deep(.vue-grid-item) {
  transition: all 200ms ease;
  transition-property: left, top, width, height;
}

:deep(.vue-grid-item.cssTransforms) {
  transition-property: transform, width, height;
}

:deep(.vue-grid-item.resizing) {
  opacity: 0.9;
  z-index: 100;
  box-shadow: 0 0 10px rgba(0,0,0,0.2);
}
</style>
