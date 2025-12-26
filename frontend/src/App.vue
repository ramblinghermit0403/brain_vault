<script setup>
import { RouterView } from 'vue-router'
import { useThemeStore } from './stores/theme'

// Initialize theme store to ensure dark mode preference persists on reload
const themeStore = useThemeStore()
</script>

<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-gray-100">
    <RouterView />
  </div>
</template>

<style>
/* Global styles are imported in main.js via style.css */
</style>
