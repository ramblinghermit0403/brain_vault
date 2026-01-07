<template>
  <div class="min-h-screen bg-white text-black font-sans flex flex-col items-center py-20 px-6">
    <div class="max-w-2xl w-full space-y-12">
      <!-- Header -->
      <div class="text-center space-y-4">
        <h1 class="text-4xl font-bold tracking-tight">Welcome to Brain Vault</h1>
        <p class="text-gray-500 text-lg">Let's set up your second brain.</p>
      </div>

      <!-- Steps Progress -->
      <div class="flex items-center justify-between border-b border-gray-100 pb-8">
        <div v-for="step in 3" :key="step" class="flex items-center gap-2">
            <div :class="[
                'w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold border transition-colors',
                currentStep >= step ? 'bg-black text-white border-black' : 'bg-white text-gray-300 border-gray-200'
            ]">
                {{ step }}
            </div>
            <span :class="[
                'text-sm font-medium',
                currentStep >= step ? 'text-black' : 'text-gray-300'
            ]">
                {{ getStepTitle(step) }}
            </span>
        </div>
      </div>

      <!-- Step 1: Extension -->
      <div v-if="currentStep === 1" class="space-y-8 animate-fade-in">
        <div class="text-center space-y-2">
           <h2 class="text-2xl font-semibold">Install the Browser Extension</h2>
           <p class="text-gray-500">Capture everything from the web with one click.</p>
        </div>
        
        <div class="bg-gray-50 border border-gray-200 p-8 rounded-none text-center space-y-6">
            <div class="mx-auto w-16 h-16 bg-white border border-gray-200 flex items-center justify-center rounded-xl shadow-sm">
                <!-- Simple icon -->
                <svg class="w-8 h-8 text-black" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"></path></svg>
            </div>
            <div>
                 <a href="#" target="_blank" class="inline-flex items-center gap-2 px-6 py-3 bg-black text-white font-bold hover:bg-gray-800 transition-colors">
                    <span>Download Extension</span>
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path></svg>
                </a>
                <p class="text-xs text-gray-400 mt-2">Requires Chrome / Brave / Edge</p>
            </div>
        </div>

        <button @click="nextStep" class="w-full py-3 border border-gray-200 font-medium hover:bg-gray-50 transition-colors text-gray-600">
            Skip for now
        </button>
      </div>

      <!-- Step 2: Cloud Settings -->
      <div v-else-if="currentStep === 2" class="space-y-8 animate-fade-in">
        <div class="text-center space-y-2">
           <h2 class="text-2xl font-semibold">Connect Your AI</h2>
           <p class="text-gray-500">Add an API Key to enable smart tagging and chat.</p>
        </div>

        <div class="space-y-4">
             <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">OpenAI API Key <span class="text-gray-400 font-normal">(Optional)</span></label>
                <input v-model="apiKey" type="password" placeholder="sk-..." class="w-full px-4 py-3 border border-gray-300 focus:outline-none focus:border-black transition-colors" />
                <p class="text-xs text-gray-400 mt-1">Stored securely using AES-256 encryption.</p>
             </div>
             
             <!-- Gemini / Bedrock toggles could go here -->
        </div>

        <div class="flex gap-4">
             <button @click="saveKeyAndNext" class="flex-1 py-3 bg-black text-white font-bold hover:bg-gray-800 transition-colors">
                Save & Continue
            </button>
            <button @click="nextStep" class="py-3 px-6 border border-gray-200 font-medium hover:bg-gray-50 transition-colors text-gray-600">
                Skip
            </button>
        </div>
      </div>

      <!-- Step 3: First Memory -->
      <div v-else-if="currentStep === 3" class="space-y-8 animate-fade-in">
        <div class="text-center space-y-2">
           <h2 class="text-2xl font-semibold">Create Your First Memory</h2>
           <p class="text-gray-500">What's on your mind? Or paste a link.</p>
        </div>

        <div>
            <textarea v-model="firstMemory" class="w-full h-40 p-4 border border-gray-300 focus:outline-none focus:border-black resize-none" placeholder="E.g. Project Idea: A smart gardening system..."></textarea>
        </div>

        <button @click="finish" class="w-full py-3 bg-black text-white font-bold hover:bg-gray-800 transition-colors">
            Finish Setup
        </button>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../stores/auth'; // You might need this to save settings
import api from '../services/api';
import { useToast } from 'vue-toastification';

const router = useRouter();
const toast = useToast();
const currentStep = ref(1);

const apiKey = ref('');
const firstMemory = ref('');

const getStepTitle = (step) => {
    switch(step) {
        case 1: return 'Extension';
        case 2: return 'Connect';
        case 3: return 'First Memory';
    }
};

const nextStep = () => {
    currentStep.value++;
};

const saveKeyAndNext = async () => {
    if (apiKey.value.trim()) {
        try {
            await api.post('/user/keys', {
                provider: 'openai', // Defaulting for simple onboarding
                api_key: apiKey.value,
                is_active: true
            });
            toast.success('Key saved!');
        } catch (e) {
            console.error(e);
            toast.error('Failed to save key, but continuing.');
        }
    }
    nextStep();
};

const finish = async () => {
    if (firstMemory.value.trim()) {
        try {
             await api.post('/memory/', {
                title: 'First Memory',
                content: firstMemory.value,
                tags: ['onboarding']
            });
            toast.success('Memory created!');
        } catch (e) {
             console.error(e);
        }
    }
    router.push('/dashboard');
};
</script>

<style scoped>
.animate-fade-in {
    animation: fadeIn 0.5s ease-out;
}
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}
</style>
