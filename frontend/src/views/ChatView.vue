

<script setup>
import { ref, onMounted, nextTick, watch, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useChatStore } from '../stores/chat';
import { useAuthStore } from '../stores/auth';
import { marked } from 'marked';
import NavBar from '../components/NavBar.vue';
import ConfirmationModal from '../components/ConfirmationModal.vue';
import { useToast } from 'vue-toastification';

const chatStore = useChatStore();
const authStore = useAuthStore();
const router = useRouter();
const toast = useToast();

const inputContent = ref('');
const messagesContainer = ref(null);
const modelTemperature = ref(0.7);
const maxTokens = ref(2048);
const showHistory = ref(window.innerWidth >= 768); // Default open on desktop
const showControls = ref(true);

// Initialize
onMounted(async () => {
   await chatStore.fetchSessions();
});

// Auto-scroll
watch(() => chatStore.messages.length, () => {
   nextTick(() => {
     scrollToBottom();
   });
});
watch(() => chatStore.thinking, () => {
   nextTick(() => {
     scrollToBottom();
   });
});

function scrollToBottom() {
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
  }
}

function formatDate(dateStr) {
   if (!dateStr) return '';
   const date = new Date(dateStr);
   return new Intl.DateTimeFormat('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' }).format(date);
}

function renderMarkdown(text) {
  return marked(text || '');
}

async function createNewChat() {
   await chatStore.createSession();
}

async function selectSession(id) {
   await chatStore.selectSession(id);
}

async function handleSend() {
   const content = inputContent.value.trim();
   if (!content || chatStore.thinking) return;
   
   // Create session if none exists (e.g. from Landing Page)
   if (!chatStore.currentSession) {
      await chatStore.createSession();
   }
   
   inputContent.value = '';
   await chatStore.sendMessage(content, modelTemperature.value, maxTokens.value);
}

const showDeleteModal = ref(false);

function handleClearHistory() {
  showDeleteModal.value = true;
}

async function confirmClearHistory() {
    await chatStore.clearHistory();
    inputContent.value = '';
    showDeleteModal.value = false;
}

async function copyToClipboard(text) {
    try {
        await navigator.clipboard.writeText(text);
        toast.success("Copied to clipboard");
    } catch (err) {
        toast.error("Failed to copy");
    }
}

async function handleFeedback(messageId, type) {
    await chatStore.sendFeedback(messageId, type);
    toast.success("Feedback submitted");
}


</script>

<template>
  <div class="h-screen flex flex-col bg-gray-50 dark:bg-app text-gray-900 dark:text-gray-100 font-sans transition-colors duration-300">
    <NavBar />

    <div class="flex-1 flex overflow-hidden relative">
      <!-- LEFTSIDEBAR: HISTORY -->
      <transition enter-active-class="transition-transform duration-300 ease-in-out" enter-from-class="-translate-x-full" enter-to-class="translate-x-0" leave-active-class="transition-transform duration-300 ease-in-out" leave-from-class="translate-x-0" leave-to-class="-translate-x-full">
        <aside v-if="showHistory" class="w-72 bg-white dark:bg-surface border-r border-gray-200 dark:border-border flex flex-col shrink-0 absolute md:static z-20 h-full shadow-lg md:shadow-none">
          <div class="p-4 border-b border-gray-100 dark:border-border flex justify-between items-center">
            <h3 class="font-semibold flex items-center gap-2 text-gray-700 dark:text-gray-200">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
              Chat History
            </h3>
            <button @click="showHistory = false" class="md:hidden text-gray-400 hover:text-gray-600">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" /></svg>
            </button>
          </div>
          
          <div class="p-4">
            <button @click="createNewChat" class="w-full py-2.5 px-4 bg-white dark:bg-surface border border-gray-200 dark:border-border rounded-lg text-gray-600 dark:text-gray-300 font-medium hover:border-black hover:text-black dark:hover:border-white dark:hover:text-white transition-colors flex items-center justify-center gap-2 shadow-sm">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" /></svg>
              New Chat
            </button>
          </div>

          <div class="flex-1 overflow-y-auto px-2 pb-4 space-y-1">
             <button
              v-for="session in chatStore.sessions"
              :key="session.id"
              @click="selectSession(session.id);" 
              class="w-full text-left px-3 py-3 rounded-lg hover:bg-gray-50 dark:hover:bg-surface-2 transition-all group relative border border-transparent"
              :class="{'bg-gray-100 border-gray-200 dark:bg-surface-2 dark:border-gray-700': chatStore.currentSession?.id === session.id}"
            >
              <p class="text-sm font-medium text-gray-800 dark:text-gray-200 truncate pr-4">{{ session.title || 'Untitled Chat' }}</p>
              <p class="text-xs text-gray-400 dark:text-gray-500 mt-0.5">{{ formatDate(session.updated_at) }}</p>
            </button>
          </div>
          
           <div class="p-4 border-t border-gray-100 dark:border-border">
             <button @click="handleClearHistory" class="w-full py-2 text-xs text-gray-400 hover:text-red-500 transition-colors">Clear History</button>
           </div>
        </aside>
      </transition>

      <!-- MAIN CHAT AREA -->
      <main class="flex-1 flex flex-col min-w-0 bg-white dark:bg-app relative">
        <!-- Background Pattern for Landing State -->
        <div v-if="chatStore.messages.length === 0" class="absolute inset-0 z-0 pointer-events-none opacity-40" 
             style="background-image: radial-gradient(#cbd5e1 1px, transparent 1px); background-size: 40px 40px;">
        </div>

        <!-- Toggle Buttons -->
        <div class="absolute top-4 left-4 z-50">
           <button @click="showHistory = !showHistory" class="p-2 bg-white dark:bg-surface rounded-md shadow-md border border-gray-200 dark:border-border text-gray-600 hover:text-gray-900 transition-colors"><svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" /></svg></button>
        </div>
        <div class="absolute top-4 right-4 z-10 lg:hidden">
           <button @click="showControls = !showControls" class="p-2 bg-white dark:bg-surface rounded-md shadow-md border border-gray-200 dark:border-border text-gray-600"><svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4" /></svg></button>
        </div>



        <!-- Messages (Standard View) -->
        <div v-if="chatStore.messages.length > 0" class="flex-1 overflow-y-auto p-4 md:p-8 scroll-smooth z-10" ref="messagesContainer">
           <div class="space-y-6 max-w-3xl mx-auto">
              <template v-for="msg in chatStore.messages" :key="msg.id">
                 <!-- USER -->
                 <div v-if="msg.role === 'user'" class="flex justify-end gap-3">
                    <div class="max-w-[85%]">
                       <div class="bg-black dark:bg-white text-white dark:text-black px-5 py-3 rounded-2xl rounded-tr-sm shadow-sm md:shadow-md text-sm md:text-base leading-relaxed">
                          <p class="whitespace-pre-wrap">{{ msg.content }}</p>
                       </div>
                       <div class="text-right mt-1 text-[10px] text-gray-400 font-medium tracking-wide mr-1">{{ formatDate(msg.created_at).split(',')[1] || 'Now' }}</div>
                    </div>

                 </div>

                 <!-- AI -->
                 <div v-else-if="msg.role === 'assistant'" class="flex justify-start gap-4">
                    <div class="w-8 h-8 rounded-full bg-white border border-gray-200 shrink-0 mt-1 shadow-sm">
                       <img src="/image.svg" alt="AI" />
                    </div>
                    <div class="max-w-[85%]">
                        <div class="bg-gray-100 dark:bg-surface-2 dark:text-gray-100 px-6 py-4 rounded-2xl rounded-tl-sm shadow-sm text-sm md:text-base leading-relaxed text-gray-800">
                          <div class="prose prose-sm max-w-none dark:prose-invert" v-html="renderMarkdown(msg.content)"></div>
                       </div>
                       <!-- Sources/Actions -->
                       <!-- Sources/Actions -->
                       <div class="mt-2 pl-1 flex items-center gap-2 text-xs text-gray-400">
                          <!-- Copy -->
                          <button @click="copyToClipboard(msg.content)" class="flex items-center gap-1 hover:text-gray-600 dark:hover:text-gray-200 transition-colors p-1 rounded">
                              <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" /></svg>
                              Copy
                          </button>
                          
                          <span class="text-gray-300 dark:text-gray-700">|</span>

                          <!-- Feedback -->
                          <div class="flex items-center gap-1">
                              <button @click="handleFeedback(msg.id, 'up')" class="hover:text-gray-600 dark:hover:text-gray-200 p-1 rounded transition-colors group">
                                  <svg class="w-4 h-4 group-active:scale-90 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 10h4.764a2 2 0 011.789 2.894l-3.5 7A2 2 0 0115.263 21h-4.017c-.163 0-.326-.02-.485-.06L7 20m7-10V5a2 2 0 00-2-2h-.095c-.5 0-.905.405-.905.905 0 .714-.211 1.412-.608 2.006L7 11v9m7-10h-2M7 20H5a2 2 0 01-2-2v-6a2 2 0 012-2h2.5" /></svg>
                              </button>
                              <button @click="handleFeedback(msg.id, 'down')" class="hover:text-gray-600 dark:hover:text-gray-200 p-1 rounded transition-colors group">
                                  <svg class="w-4 h-4 group-active:scale-90 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14H5.236a2 2 0 01-1.789-2.894l3.5-7A2 2 0 018.736 3h4.018a2 2 0 01.485.06l3.76.94m-7 10v5a2 2 0 002 2h.095c.5 0 .905-.405.905-.905 0-.714.211-1.412.608-2.006L17 13V4m-7 10h2m5-10h2a2 2 0 012 2v6a2 2 0 01-2 2h-2.5" /></svg>
                              </button>
                          </div>
                       </div>
                    </div>
                 </div>
              </template>
           </div>
           
           <!-- Thinking Indicator (Outside space-y for custom spacing) -->
           <div v-if="chatStore.thinking" class="max-w-3xl mx-auto mt-2 flex justify-start gap-4 animate-pulse opacity-70">
              <div class="w-8 h-8 rounded-full bg-gray-200 dark:bg-gray-700 shrink-0"></div>
              <div class="bg-gray-100 dark:bg-surface-2 h-12 w-48 rounded-2xl rounded-tl-sm"></div>
           </div>
        </div>

        <!-- BOTTOM BAR (Standard View) -->
        <div class="px-6 pt-2 pb-8 z-10" v-if="chatStore.messages.length > 0 && chatStore.currentSession">
           <div class="max-w-3xl mx-auto">
              <div class="bg-gray-100 dark:bg-surface-2 rounded-3xl transition-all focus-within:ring-2 focus-within:ring-gray-200 dark:focus-within:ring-gray-700 p-2 border border-transparent focus-within:border-gray-300 dark:focus-within:border-gray-600">
                 <textarea
                   v-model="inputContent"
                   @keydown.enter.prevent="handleSend"
                   placeholder="Type your message here..."
                   rows="1"
                   class="w-full bg-transparent border-0 focus:border-0 focus:ring-0 outline-none focus:outline-none rounded-2xl px-4 py-2 text-gray-900 dark:text-white resize-none max-h-32 placeholder-gray-500 dark:placeholder-gray-400"
                 ></textarea>
                 
                 <div class="px-2 pb-1 flex justify-end items-center text-xs text-gray-500 mt-1">
                    <div class="flex items-center gap-3">
                       <div class="relative group">
                          <select 
                             v-model="chatStore.selectedModel" 
                             class="appearance-none bg-transparent border-none text-xs text-gray-700 dark:text-gray-300 font-medium font-sans cursor-pointer focus:ring-0 pr-6 hover:text-black dark:hover:text-white transition-colors"
                             title="Select AI Model"
                          >
                             <option v-for="model in chatStore.availableModels" :key="model.id" :value="model.id" class="text-gray-900 bg-white dark:bg-surface dark:text-gray-100">{{ model.name }}</option>
                          </select>
                          <svg class="w-3 h-3 absolute right-0 top-1/2 -translate-y-1/2 pointer-events-none text-gray-400 group-hover:text-gray-600 transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" /></svg>
                       </div>
                       
                       <button 
                         @click="handleSend"
                         :disabled="!inputContent.trim() || chatStore.thinking"
                         class="p-2 bg-black dark:bg-white text-white dark:text-black rounded-full hover:bg-gray-900 dark:hover:bg-gray-200 disabled:opacity-50 transition-transform active:scale-95 shadow-md flex items-center justify-center w-8 h-8"
                       >
                         <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 10l7-7m0 0l7 7m-7-7v18" /></svg>
                       </button>
                    </div>
                 </div>
              </div>
              <p class="text-center text-xs text-gray-400 mt-2">Ctrl + Enter to send</p>
           </div>
        </div>


        <!-- LANDING INPUT (Empty State) -->
        <div v-else class="flex-1 flex flex-col items-center justify-center p-4 z-10">
           <div class="max-w-3xl w-full">
              <h1 class="text-4xl font-bold text-gray-900 dark:text-white mb-8 text-left">
                 Welcome, <span class="text-black dark:text-white">{{ authStore.user?.email?.split('@')[0] || 'Traveler' }}</span>
              </h1>
              
              <div class="bg-white dark:bg-surface rounded-3xl shadow-xl border border-gray-100 dark:border-gray-700 p-2">
                 <textarea
                   v-model="inputContent"
                   @keydown.enter.prevent="handleSend"
                   placeholder="Ask your MemWyre..."
                   rows="1"
                   class="w-full bg-transparent border-0 focus:border-0 focus:ring-0 outline-none focus:outline-none rounded-2xl px-6 py-4 text-lg text-gray-900 dark:text-white resize-none min-h-[80px] placeholder-gray-400"
                 ></textarea>

                 <div class="px-4 pb-2 flex justify-end items-center text-sm text-gray-500">
                    <div class="flex items-center gap-4">
                       <div class="relative group">
                          <select 
                             v-model="chatStore.selectedModel" 
                             class="appearance-none bg-transparent border-none text-sm text-gray-700 dark:text-gray-300 font-medium font-sans cursor-pointer focus:ring-0 pr-6 hover:text-black dark:hover:text-white transition-colors"
                             title="Select AI Model"
                          >
                             <option v-for="model in chatStore.availableModels" :key="model.id" :value="model.id" class="text-gray-900 bg-white dark:bg-surface dark:text-gray-100">{{ model.name }}</option>
                          </select>
                          <svg class="w-3 h-3 absolute right-0 top-1/2 -translate-y-1/2 pointer-events-none text-gray-400 group-hover:text-gray-600 transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" /></svg>
                       </div>
                       
                       <button 
                         @click="handleSend"
                         :disabled="!inputContent.trim() || chatStore.thinking"
                         class="p-2 bg-black dark:bg-white text-white dark:text-black rounded-full hover:bg-gray-800 dark:hover:bg-gray-200 disabled:opacity-50 transition-transform active:scale-95 shadow-md flex items-center justify-center w-10 h-10"
                       >
                         <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 10l7-7m0 0l7 7m-7-7v18" /></svg>
                       </button>
                    </div>
                 </div>
              </div>
           </div>
        </div>
      </main>

      <!-- RIGHT SIDEBAR: CONTROLS -->
      <transition enter-active-class="transition-transform duration-300 ease-in-out" enter-from-class="translate-x-full" enter-to-class="translate-x-0" leave-active-class="transition-transform duration-300 ease-in-out" leave-from-class="translate-x-0" leave-to-class="translate-x-full">
         <aside v-if="showControls" class="w-80 bg-white dark:bg-surface border-l border-gray-200 dark:border-border hidden lg:flex flex-col shrink-0">
            <div class="p-4 border-b border-gray-100 dark:border-border flex justify-between items-center">
               <h3 class="font-semibold flex items-center gap-2 text-gray-700 dark:text-gray-200">
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                  Context & Controls
               </h3>
               <!-- Removed close button -->
            </div>
            
            <div class="p-6 space-y-8 overflow-y-auto">
               <!-- Model Temp -->
               <div>
                  <div class="flex justify-between items-center mb-2">
                     <label class="text-sm font-medium text-gray-700 dark:text-gray-300">Model Temperature</label>
                     <span class="text-xs font-mono bg-gray-100 dark:bg-surface-2 px-2 py-0.5 rounded text-gray-600">{{ modelTemperature }}</span>
                  </div>
                  <input type="range" min="0" max="1" step="0.1" v-model="modelTemperature" class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-black dark:accent-white">
                  <p class="text-xs text-gray-400 mt-2">Higher values make usage more creative.</p>
               </div>

               <!-- Max Tokens -->
               <div>
                  <label class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2 block">Max Tokens</label>
                  <input type="number" v-model="maxTokens" class="w-full px-3 py-2 border border-gray-200 dark:border-border rounded-lg text-sm bg-gray-50 dark:bg-surface-2 focus:ring-1 focus:ring-black dark:focus:ring-white focus:border-black dark:focus:border-white">
                  <p class="text-xs text-gray-400 mt-1">{{ maxTokens }} tokens</p>
               </div>
               
               <hr class="border-gray-100 dark:border-border">

               <!-- Context Info -->
               <div>
                  <h4 class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">Current Document / Context</h4>
                  
                  <div v-if="chatStore.currentContext.length > 0" class="space-y-2">
                     <div v-for="(source, index) in chatStore.currentContext" :key="index" class="p-3 bg-gray-50 dark:bg-surface-2 rounded-lg border border-gray-100 dark:border-border flex justify-between items-center gap-2">
                        <div class="overflow-hidden">
                           <p class="text-sm text-black dark:text-white font-medium mb-0.5 truncate" :title="source.title || source">{{ source.title || source }}</p>
                           <p class="text-xs text-gray-500">Retrieval Source</p>
                        </div>
                        <button 
                           v-if="source.id" 
                           @click="router.push({name: 'editor', params: {id: source.id}})" 
                           class="shrink-0 text-xs bg-white dark:bg-app border border-gray-200 dark:border-gray-700 text-gray-600 dark:text-gray-300 px-2 py-1 rounded hover:bg-gray-50 dark:hover:bg-surface transition-colors"
                        >
                           Open ↗
                        </button>
                     </div>
                  </div>
                  
                  <div v-else class="p-3 bg-gray-50 dark:bg-surface-2 rounded-lg border border-gray-100 dark:border-border">
                     <p class="text-xs text-gray-500 italic mb-2">No active document context.</p>
                     <p class="text-xs text-gray-400">
                        LLMs are a type of artificial intelligence model designed to understand and generate human language...
                     </p>
                  </div>
               </div>
            </div>
         </aside>
      </transition>
    </div>
    
    <ConfirmationModal
      :is-open="showDeleteModal"
      title="Clear History"
      message="Are you sure you want to delete all chat history? This cannot be undone."
      confirm-text="Clear History"
      @confirm="confirmClearHistory"
      @cancel="showDeleteModal = false"
    />
  </div>
</template>

<style scoped>
/* Custom scrollbar for message area */
.overflow-y-auto::-webkit-scrollbar {
  width: 6px;
}
.overflow-y-auto::-webkit-scrollbar-track {
  background: transparent;
}
.overflow-y-auto::-webkit-scrollbar-thumb {
  background-color: rgba(0, 0, 0, 0.1);
  border-radius: 20px;
}
</style>
