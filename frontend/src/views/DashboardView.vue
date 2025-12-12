<template>
  <div class="h-screen flex flex-col bg-gray-50 dark:bg-app transition-colors duration-300 font-sans overflow-hidden">
    <NavBar />

    <main class="flex-1 overflow-y-auto w-full pt-8 pb-12 no-scrollbar">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col min-h-full">
          <div class="mb-8">
            <h1 class="text-3xl font-bold text-gray-900 dark:text-white">Good {{ timeOfDay }}, {{ user?.name || 'User' }}</h1>
            <p class="mt-1 text-gray-500 dark:text-text-secondary">Welcome back to your Brain Vault. Here's a quick overview.</p>
          </div>

          <div class="grid grid-cols-1 lg:grid-cols-3 gap-8 flex-1">
              <!-- Left Column: Unified Document List (span 2 cols) -->
              <div class="lg:col-span-2 flex flex-col">
                  <div class="bg-white dark:bg-surface rounded-xl shadow-sm border border-gray-100 dark:border-border overflow-hidden flex-1 flex flex-col h-[600px]">
                      <UnifiedDocumentList class="flex-1" />
                  </div>
              </div>


               <!-- Right Column: Actions & Widgets -->
               <div class="flex flex-col gap-6 h-full">
                  <!-- Ask Brain Vault -->
                   <div class="bg-white dark:bg-surface rounded-xl shadow-sm border border-gray-100 dark:border-border p-6 flex-1 flex flex-col">
                       <h3 class="text-lg font-semibold text-gray-900 dark:text-text-primary mb-2 flex items-center gap-2">
                            <svg class="w-5 h-5 text-gray-500 dark:text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" /></svg>
                           Ask Your Brain Vault
                       </h3>
                       <p class="text-sm text-gray-500 dark:text-text-secondary mb-4">Instantly retrieve information from your knowledge base.</p>
                      <RetrievalTest :embedded="true" class="flex-1" />
                  </div>

                  <!-- File Upload -->
                  <div class="bg-white dark:bg-surface rounded-xl shadow-sm border border-gray-100 dark:border-border p-6 flex-1 flex flex-col">
                      <h3 class="text-lg font-semibold text-gray-900 dark:text-text-primary mb-2 flex items-center gap-2">
                           <svg class="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" /></svg>
                           File Upload
                      </h3>
                      <p class="text-sm text-gray-500 dark:text-text-secondary mb-4">Drag and drop or select files to add to your vault.</p>
                      <FileUpload class="flex-1" />
                  </div>
              </div>
          </div>
      </div>
    </main>
    <QuickActions @open-review="showDailyReview = true" />
    <DailyReviewModal v-if="showDailyReview" @close="showDailyReview = false" />
  </div>
</template>

<script setup>
import { onMounted, computed, ref } from 'vue';
import NavBar from '../components/NavBar.vue';
import UnifiedDocumentList from '../components/UnifiedDocumentList.vue';
import QuickActions from '../components/QuickActions.vue';
import FileUpload from '../components/FileUpload.vue';
import RetrievalTest from '../components/RetrievalTest.vue';
import DailyReviewModal from '../components/DailyReviewModal.vue';
import { createTour } from '../tour';
import { useInboxStore } from '../stores/inbox';
import { useAuthStore } from '../stores/auth';

const inboxStore = useInboxStore();
const authStore = useAuthStore();
const user = computed(() => authStore.user);
const showDailyReview = ref(false);

const timeOfDay = computed(() => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Morning';
    if (hour < 18) return 'Afternoon';
    return 'Evening';
});

inboxStore.fetchInbox();
inboxStore.connectWebSocket();

onMounted(() => {
    const tourCompleted = localStorage.getItem('tour_completed');
    if (!tourCompleted) {
        const driver = createTour();
        driver.drive();
        localStorage.setItem('tour_completed', 'true');
    }
});
</script>
