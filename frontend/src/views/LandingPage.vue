<template>
  <div class="min-h-screen bg-white dark:bg-black text-black dark:text-white transition-colors duration-300 font-sans selection:bg-black selection:text-white dark:selection:bg-white dark:selection:text-black">
    <!-- Brand Reveal Intro -->
    <div v-if="showIntro" class="fixed inset-0 z-[100] flex items-center justify-center bg-black transition-opacity duration-1000" :class="{ 'opacity-0': fadeOut }">
        <div class="relative flex flex-col items-center">
            <!-- Glow Effect -->
            <div class="absolute inset-0 bg-white/20 blur-[100px] rounded-full scale-0 transition-transform duration-[2000ms] ease-out" :class="{ 'scale-150': startGlow }"></div>
            
            <!-- Logo Wordmark -->
            <div class="relative z-10 text-center">
                <h1 class="text-6xl md:text-8xl font-black tracking-tighter text-transparent bg-clip-text bg-gradient-to-b from-white to-gray-400 opacity-0 translate-y-4 transition-all duration-1000 ease-out" :class="{ 'opacity-100 translate-y-0': showLogo }">
                    MEMWYRE
                </h1>
                <p class="mt-4 text-xl md:text-2xl font-light tracking-[0.2em] text-gray-400 opacity-0 transition-opacity duration-1000 delay-500" :class="{ 'opacity-100': showTagline }">
                    YOUR SECOND BRAIN,<br>
                    <span class="text-white font-bold">SUPERCHARGED.</span>
                </p>
            </div>
        </div>
    </div>

    <!-- Navigation -->
    <nav class="fixed w-full z-50 bg-white/90 dark:bg-black/90 backdrop-blur-sm border-b border-gray-100 dark:border-gray-800">
      <div class="max-w-7xl mx-auto px-6 lg:px-8">
        <div class="flex justify-between items-center h-20">
          <router-link to="/" class="flex items-center group">
            <img src="/image.svg" alt="MemWyre" class="w-8 h-8 rounded-lg mr-3 group-hover:scale-105 transition-transform duration-300" />
            <span class="text-xl font-bold tracking-tight">MemWyre</span>
          </router-link>
          
          <div class="hidden md:flex items-center space-x-8 text-sm font-medium">
            <a href="#features" class="text-gray-500 hover:text-black dark:hover:text-white transition-colors">Features</a>
            <a href="#workflow" class="text-gray-500 hover:text-black dark:hover:text-white transition-colors">Workflow</a>
            <a href="#ecosystem" class="text-gray-500 hover:text-black dark:hover:text-white transition-colors">Ecosystem</a>
            <a href="#faq" class="text-gray-500 hover:text-black dark:hover:text-white transition-colors">FAQ</a>
          </div>

          <div class="flex items-center gap-4">
            <router-link to="/login" class="text-sm font-medium text-gray-500 hover:text-black dark:hover:text-white transition-colors">
              Log in
            </router-link>
            <router-link to="/register" class="px-5 py-2.5 bg-black dark:bg-white text-white dark:text-black text-sm font-bold rounded-full hover:opacity-90 transition-opacity">
              Get Started
            </router-link>
          </div>
        </div>
      </div>
    </nav>
    
    <!-- Hero Section -->
    <div class="pt-40 pb-20 lg:pt-52 lg:pb-32 px-6 lg:px-8 max-w-7xl mx-auto">
      <div class="flex flex-col items-start text-left">
        <!-- Hero Content -->
        <div class="max-w-4xl">
            <h1 class="text-6xl lg:text-8xl font-extrabold tracking-tighter leading-[0.9] text-black dark:text-white mb-8">
            Your Second Brain,<br>
            <span class="bg-black text-white dark:bg-white dark:text-black px-1 lg:px-4 leading-normal">Supercharged.</span>
            </h1>
            <p class="text-xl lg:text-2xl text-gray-500 dark:text-gray-400 leading-relaxed mb-12 max-w-2xl">
            Capture thoughts, ingest documents, and chat with your personal knowledge base. Secure, private, and minimal.
            </p>
            <div class="flex flex-col sm:flex-row gap-4 justify-start">
            <router-link to="/register" class="px-8 py-4 bg-black dark:bg-white text-white dark:text-black text-lg font-bold rounded-full hover:translate-y-[-2px] transition-transform duration-300 flex items-center justify-center gap-2">
                Start Building
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3" /></svg>
            </router-link>
            <a href="#features" class="px-8 py-4 border border-gray-200 dark:border-gray-800 text-black dark:text-white text-lg font-bold rounded-full hover:bg-gray-50 dark:hover:bg-gray-900 transition-colors flex items-center justify-center">
                How it works
            </a>
            </div>
        </div>
      </div>
    </div>

    <!-- Divider -->
    <div class="w-full h-px bg-gray-100 dark:bg-gray-900"></div>

    <!-- Features Grid -->
    <div id="features" class="py-32 px-6 lg:px-8 max-w-7xl mx-auto">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-x-8 gap-y-16">
        <div class="group">
          <div class="w-12 h-12 flex items-center justify-center border border-gray-200 dark:border-gray-800 rounded-xl mb-6 group-hover:bg-black group-hover:text-white dark:group-hover:bg-white dark:group-hover:text-black transition-colors duration-300">
             <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" /></svg>
          </div>
          <h3 class="text-2xl font-bold mb-3">Memory Map</h3>
          <p class="text-gray-500 dark:text-gray-400 leading-relaxed">
            Visualize connections between your thoughts. Our intelligent tagging system links related concepts automatically, revealing hidden patterns.
          </p>
        </div>

        <div class="group">
          <div class="w-12 h-12 flex items-center justify-center border border-gray-200 dark:border-gray-800 rounded-xl mb-6 group-hover:bg-black group-hover:text-white dark:group-hover:bg-white dark:group-hover:text-black transition-colors duration-300">
            <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" /></svg>
          </div>
          <h3 class="text-2xl font-bold mb-3">Contextual Chat</h3>
          <p class="text-gray-500 dark:text-gray-400 leading-relaxed">
            Don't just search—converse. Ask questions and get answers grounded in your own notes, documents, and code snippets.
          </p>
        </div>

        <div class="group">
          <div class="w-12 h-12 flex items-center justify-center border border-gray-200 dark:border-gray-800 rounded-xl mb-6 group-hover:bg-black group-hover:text-white dark:group-hover:bg-white dark:group-hover:text-black transition-colors duration-300">
            <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" /></svg>
          </div>
          <h3 class="text-2xl font-bold mb-3">Unified Ingestion</h3>
          <p class="text-gray-500 dark:text-gray-400 leading-relaxed">
            Bring everything together. Import PDFs, scrape web pages, add YouTube videos, and sync your notes into one central vault.
          </p>
        </div>
      </div>
    </div>

    <!-- Workflow Section -->
     <div id="workflow" class="py-32 bg-gray-50 dark:bg-white/5 border-y border-gray-100 dark:border-gray-900">
      <div class="max-w-7xl mx-auto px-6 lg:px-8">
        <div class="mb-20">
          <h2 class="text-sm font-bold uppercase tracking-widest text-gray-400 mb-4">Workflow</h2>
          <p class="text-4xl lg:text-5xl font-extrabold tracking-tight">Structured for flow.</p>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
            <div class="space-y-12">
                <div class="flex gap-6">
                    <span class="text-4xl font-light text-gray-200 dark:text-gray-700">01</span>
                    <div>
                        <h3 class="text-2xl font-bold mb-2">Ingest</h3>
                        <p class="text-gray-500 dark:text-gray-400">Drag & drop PDFs, paste URLs, or sync from your browser. We handle the parsing.</p>
                    </div>
                </div>
                 <div class="flex gap-6">
                    <span class="text-4xl font-light text-gray-200 dark:text-gray-700">02</span>
                    <div>
                        <h3 class="text-2xl font-bold mb-2">Connect</h3>
                        <p class="text-gray-500 dark:text-gray-400">AI automatically tags and links your content, creating a navigable graph of knowledge.</p>
                    </div>
                </div>
                 <div class="flex gap-6">
                    <span class="text-4xl font-light text-gray-200 dark:text-gray-700">03</span>
                    <div>
                        <h3 class="text-2xl font-bold mb-2">Retrieve</h3>
                        <p class="text-gray-500 dark:text-gray-400">Ask questions naturally. Get synthesized answers with direct citations to your sources.</p>
                    </div>
                </div>
            </div>
            
            <div class="relative group">
                <div class="absolute -inset-1 bg-gradient-to-r from-gray-200 to-gray-100 dark:from-gray-800 dark:to-gray-900 rounded-2xl blur opacity-25 group-hover:opacity-50 transition duration-1000"></div>
                <div class="relative bg-white dark:bg-black border border-gray-100 dark:border-gray-800 rounded-2xl p-8 shadow-2xl">
                    <div class="font-mono text-sm space-y-4">
                        <div class="flex items-center gap-2 border-b border-gray-100 dark:border-gray-800 pb-4 mb-4">
                            <span class="w-3 h-3 rounded-full bg-black dark:bg-white"></span>
                            <span class="text-gray-400">Ask MemWyre</span>
                        </div>
                        <p class="text-gray-800 dark:text-gray-200">
                            > How do I implement the new auth flow?<br><br>
                            <span class="text-gray-400">Searching 3 documents...</span><br>
                            <span class="text-blue-500">Found matches in "Auth Specs v2" and "API Docs".</span><br><br>
                            Based on "Auth Specs v2", you should use the OAuth2 provider pattern. Here is the implementation snippet...
                        </p>
                    </div>
                </div>
            </div>
        </div>
      </div>
     </div>

    <!-- Ecosystem -->
    <div id="ecosystem" class="py-32 px-6 lg:px-8 max-w-7xl mx-auto">
        <div class="text-center max-w-3xl mx-auto mb-20">
             <h2 class="text-sm font-bold uppercase tracking-widest text-gray-400 mb-4">Ecosystem</h2>
             <p class="text-4xl lg:text-5xl font-extrabold tracking-tight mb-6">Built to extend.</p>
             <p class="text-xl text-gray-500 dark:text-gray-400">MemWyre isn't a silo. It powers your entire workflow through standard protocols.</p>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
             <div class="p-10 border border-gray-200 dark:border-gray-800 rounded-3xl hover:border-black dark:hover:border-white transition-colors duration-300">
                 <div class="w-12 h-12 bg-black dark:bg-white text-white dark:text-black rounded-lg flex items-center justify-center mb-6 font-bold text-xl">M</div>
                 <h3 class="text-2xl font-bold mb-4">MCP Server</h3>
                 <p class="text-gray-500 dark:text-gray-400 mb-8">
                     Connect MemWyre directly to Claude Desktop or any MCP-compliant client. Give your AI assistant direct access to your second brain.
                 </p>
                 <div class="bg-gray-50 dark:bg-gray-900 rounded-lg p-4 font-mono text-xs text-gray-600 dark:text-gray-400">
                     $ mcp-server-brain-vault start
                 </div>
             </div>

             <div class="p-10 border border-gray-200 dark:border-gray-800 rounded-3xl hover:border-black dark:hover:border-white transition-colors duration-300">
                 <div class="w-12 h-12 bg-black dark:bg-white text-white dark:text-black rounded-lg flex items-center justify-center mb-6 font-bold text-xl">
                      <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9" /></svg>
                 </div>
                 <h3 class="text-2xl font-bold mb-4">Browser Extension</h3>
                 <p class="text-gray-500 dark:text-gray-400 mb-8">
                     Capture the web as you browse. Save articles, documentation, or code snippets instantly without breaking your flow.
                 </p>
                 <div class="flex items-center gap-2 text-sm font-bold">
                     <span>Available for Chrome & Edge</span>
                     <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3" /></svg>
                 </div>
             </div>
        </div>
    </div>

    <!-- FAQ Section -->
    <div id="faq" class="py-32 px-6 lg:px-8 max-w-3xl mx-auto">
        <div class="text-center mb-16">
             <h2 class="text-sm font-bold uppercase tracking-widest text-gray-400 mb-4">FAQ</h2>
             <p class="text-4xl font-extrabold tracking-tight">Common questions.</p>
        </div>

        <div class="space-y-4">
            <div v-for="(faq, index) in faqs" :key="index" class="border-b border-gray-200 dark:border-gray-800 pb-4">
                <button @click="toggleFaq(index)" class="flex justify-between items-center w-full text-left py-4 group">
                    <span class="text-lg font-bold group-hover:text-gray-600 dark:group-hover:text-gray-300 transition-colors">{{ faq.question }}</span>
                    <span class="ml-4 flex-shrink-0">
                        <svg v-if="faq.isOpen" class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 12H4" /></svg>
                        <svg v-else class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" /></svg>
                    </span>
                </button>
                <div v-show="faq.isOpen" class="text-gray-500 dark:text-gray-400 pb-4 leading-relaxed">
                    {{ faq.answer }}
                </div>
            </div>
        </div>
    </div>

    <!-- Footer -->
    <footer class="border-t border-gray-100 dark:border-gray-900 py-12 bg-gray-50 dark:bg-black">
      <div class="max-w-7xl mx-auto px-6 lg:px-8 flex flex-col md:flex-row justify-between items-center gap-6">
        <div class="flex items-center gap-2">
            <img src="/image.svg" alt="MemWyre" class="w-6 h-6 rounded-lg" />
            <span class="font-bold text-sm">MemWyre</span>
        </div>
        <p class="text-sm text-gray-400">© 2025 MemWyre. Crafted for clarity.</p>
        <div class="flex gap-6">
             <a href="#" class="text-gray-400 hover:text-black dark:hover:text-white transition-colors">Twitter</a>
             <a href="#" class="text-gray-400 hover:text-black dark:hover:text-white transition-colors">GitHub</a>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';

// Intro Animation State
const showIntro = ref(true);
const fadeOut = ref(false);
const startGlow = ref(false);
const showLogo = ref(false);
const showTagline = ref(false);

onMounted(() => {
    // Sequence
    setTimeout(() => { startGlow.value = true; }, 500); // Glow emerges
    setTimeout(() => { showLogo.value = true; }, 1000); // Logo fades in
    setTimeout(() => { showTagline.value = true; }, 2000); // Tagline fades in
    
    // Hold then fade out
    setTimeout(() => { fadeOut.value = true; }, 5000);
    
    // Remove from DOM
    setTimeout(() => { showIntro.value = false; }, 6000);
});

const faqs = ref([
    {
        question: "What exactly is a 'Second Brain'?",
        answer: "A Second Brain is a personal system for recording, organizing, and retrieving the information that matters to you. MemWyre automates this process using AI to link and surface relevant info when you need it.",
        isOpen: false
    },
    {
        question: "What kind of content can I add?",
        answer: "MemWyre supports a wide range of formats. You can upload PDF documents, text files, markdown notes, and even ingest content directly from YouTube videos and web pages.",
        isOpen: false
    },
    {
        question: "How does the AI Chat work?",
        answer: "We use Retrieval-Augmented Generation (RAG). When you ask a question, MemWyre searches your documents for relevant context and feeds it to the AI, ensuring the answer is grounded in your actual data.",
        isOpen: false
    },
     {
        question: "Can I use MemWyre offline?",
        answer: "The local version of MemWyre can run entirely on your machine. However, certain AI features may require an internet connection depending on your configuration (e.g., using OpenAI vs local LLMs).",
        isOpen: false
    }
]);

const toggleFaq = (index) => {
    faqs.value[index].isOpen = !faqs.value[index].isOpen;
};
</script>

<style scoped>
html {
  scroll-behavior: smooth;
}
</style>
