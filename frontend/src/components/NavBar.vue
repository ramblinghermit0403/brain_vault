<template>
  <nav class="bg-white/80 dark:bg-surface/80 backdrop-blur-md border-b border-gray-200 dark:border-border sticky top-0 z-50 transition-colors duration-300">
    <div class="w-full px-6">
      <div class="flex justify-between h-16">
        <div class="flex items-center">
          <router-link to="/" class="flex-shrink-0 flex items-center">
            <div class="flex items-center gap-2 select-none" id="nav-logo">
                <!-- Icon -->
                <div class="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center text-white shadow-md">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>
                </div>
                <h1 class="text-xl font-bold text-blue-600 dark:text-primary">Brain Vault</h1>
            </div>
          </router-link>
        </div>

        <div class="flex items-center gap-4">
          <router-link to="/" active-class="bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-white" class="flex items-center gap-2 text-gray-500 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white px-3 py-2 rounded-md text-sm font-medium transition-colors">
             <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" /></svg>
             Dashboard
          </router-link>

          <router-link to="/inbox" active-class="bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-white" class="relative flex items-center gap-2 text-gray-500 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white px-3 py-2 rounded-md text-sm font-medium transition-colors">
             <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" /></svg>
            Inbox
            <span v-if="inboxCount > 0" class="absolute top-1.5 right-1.5 flex h-2 w-2 items-center justify-center rounded-full bg-red-500 ring-2 ring-white dark:ring-gray-800"></span>
          </router-link>

          <router-link to="/map" active-class="bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-white" class="flex items-center gap-2 text-gray-500 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white px-3 py-2 rounded-md text-sm font-medium transition-colors">
             <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" /></svg>
             Memory Map
          </router-link>

          <div class="h-6 w-px bg-gray-200 dark:bg-divider mx-2"></div>
          
          <!-- Profile Dropdown -->
          <div class="relative ml-2" v-click-outside="closeProfile">
             <button @click="toggleProfile" class="flex items-center gap-2 focus:outline-none transition-transform active:scale-95">
                 <img class="h-8 w-8 rounded-full border border-gray-200 dark:border-border transition-all" :src="userAvatar" alt="User Avatar">
             </button>

             <transition
                enter-active-class="transition ease-out duration-100"
                enter-from-class="transform opacity-0 scale-95"
                enter-to-class="transform opacity-100 scale-100"
                leave-active-class="transition ease-in duration-75"
                leave-from-class="transform opacity-100 scale-100"
                leave-to-class="transform opacity-0 scale-95"
             >
                 <div v-if="isProfileOpen" class="absolute right-0 mt-2 w-48 bg-white dark:bg-elevated rounded-lg shadow-xl py-1 ring-1 ring-black ring-opacity-5 z-50 border border-gray-100 dark:border-border">
                     <div class="px-4 py-3 border-b border-gray-100 dark:border-divider">
                         <p class="text-sm text-gray-500 dark:text-text-secondary">Signed in as</p>
                         <p class="text-sm font-medium text-gray-900 dark:text-text-primary truncate">{{ authStore.user?.email || 'Guest' }}</p>
                     </div>
                     <router-link to="/settings" class="flex items-center px-4 py-2 text-sm text-gray-700 dark:text-text-secondary hover:bg-gray-50 dark:hover:bg-surface-2 transition-colors" @click="closeProfile">
                         <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" /><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /></svg>
                         Settings
                     </router-link>
                     <button @click="logout" class="flex w-full items-center px-4 py-2 text-sm text-red-600 dark:text-danger hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors">
                         <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" /></svg>
                         Logout
                     </button>
                 </div>
             </transition>
          </div>
        </div>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { computed, ref } from 'vue';
import { useRouter } from 'vue-router';
import { useInboxStore } from '../stores/inbox';
import { useAuthStore } from '../stores/auth';

const router = useRouter();
const inboxStore = useInboxStore();
const authStore = useAuthStore();
const inboxCount = computed(() => inboxStore.count);
const isProfileOpen = ref(false);

const userAvatar = computed(() => {
  const email = authStore.user?.email || 'User';
  return `https://ui-avatars.com/api/?name=${encodeURIComponent(email)}&background=random`;
});

const toggleProfile = () => {
  isProfileOpen.value = !isProfileOpen.value;
};

const closeProfile = () => {
  if (isProfileOpen.value) isProfileOpen.value = false;
};

const logout = () => {
  localStorage.removeItem('token');
  router.push('/login');
};

// V-click-outside directive
const vClickOutside = {
  mounted(el, binding) {
    el.clickOutsideEvent = function(event) {
      if (!(el === event.target || el.contains(event.target))) {
        binding.value(event, el);
      }
    };
    document.body.addEventListener('click', el.clickOutsideEvent);
  },
  unmounted(el) {
    document.body.removeEventListener('click', el.clickOutsideEvent);
  }
};
</script>
