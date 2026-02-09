import { defineStore } from 'pinia';
import { ref } from 'vue';
import axios from 'axios';
import { useAuthStore } from './auth';
import { useToast } from 'vue-toastification';

export const useChatStore = defineStore('chat', () => {
    const sessions = ref([]);
    const currentSession = ref(null);
    const messages = ref([]);
    const isLoading = ref(false);
    const error = ref(null);
    const thinking = ref(false);
    const selectedModel = ref('apac.amazon.nova-pro-v1:0'); // Default to Nova Pro

    // Auto-migrate from deprecated models (Force check on init)
    // Enforce Nova Pro for ANY previous selection containing "gemini"
    if (selectedModel.value.includes('gemini')) {
        selectedModel.value = 'apac.amazon.nova-pro-v1:0';
    }

    // Also check local storage explicitly
    const storedModel = localStorage.getItem('chat-model');
    if (storedModel && storedModel.includes('gemini')) {
        selectedModel.value = 'apac.amazon.nova-pro-v1:0';
        localStorage.setItem('chat-model', 'apac.amazon.nova-pro-v1:0');
    }

    const availableModels = [
        { id: 'apac.amazon.nova-pro-v1:0', name: 'Amazon Nova Pro' }
    ];

    const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

    async function getAuthHeaders() {
        const authStore = useAuthStore();
        return {
            headers: {
                Authorization: `Bearer ${authStore.token}`
            }
        };
    }

    async function fetchSessions() {
        isLoading.value = true;
        try {
            const headers = await getAuthHeaders();
            const response = await axios.get(`${API_URL}/chat/sessions`, headers);
            sessions.value = response.data;
        } catch (e) {
            error.value = e.message;
        } finally {
            isLoading.value = false;
        }
    }

    async function createSession(title = "New Chat") {
        try {
            const headers = await getAuthHeaders();
            const response = await axios.post(`${API_URL}/chat/sessions`, { title }, headers);
            sessions.value.unshift(response.data);
            currentSession.value = response.data;
            messages.value = []; // Clear messages for new session
            currentContext.value = []; // Clear context
            return response.data;
        } catch (e) {
            error.value = e.message;
            const toast = useToast();
            toast.error("Failed to create new session");
        }
    }

    async function selectSession(sessionId) {
        isLoading.value = true;
        try {
            const headers = await getAuthHeaders();
            // 1. Set current session
            const session = sessions.value.find(s => s.id === sessionId);
            if (session) currentSession.value = session;

            // 2. Fetch History
            const response = await axios.get(`${API_URL}/chat/sessions/${sessionId}/history`, headers);
            messages.value = response.data;

            // 3. Restore Context from latest message
            currentContext.value = [];
            if (messages.value.length > 0) {
                // Find last message with sources
                for (let i = messages.value.length - 1; i >= 0; i--) {
                    if (messages.value[i].sources && messages.value[i].sources.length > 0) {
                        currentContext.value = messages.value[i].sources;
                        break;
                    }
                }
            }
        } catch (e) {
            error.value = e.message;
        } finally {
            isLoading.value = false;
        }
    }

    const currentContext = ref([]); // Store active context sources

    async function sendMessage(content, temperature = 0.7, maxTokens = 2048) {
        if (!currentSession.value) return;

        // Optimistic UI Update
        const tempId = Date.now();
        messages.value.push({
            id: tempId,
            role: 'user',
            content: content,
            created_at: new Date().toISOString()
        });

        thinking.value = true;
        currentContext.value = []; // Reset context for new turn

        try {
            const headers = await getAuthHeaders();
            const response = await axios.post(
                `${API_URL}/chat/sessions/${currentSession.value.id}/message`,
                {
                    content,
                    model: selectedModel.value,
                    temperature: Number(temperature),
                    max_tokens: Number(maxTokens)
                },
                headers
            );

            // Add Assistant Response
            messages.value.push(response.data);

            // Update Context if sources returned
            if (response.data.sources && response.data.sources.length > 0) {
                currentContext.value = response.data.sources;
            }

            // Move session to top of list
            const index = sessions.value.findIndex(s => s.id === currentSession.value.id);
            if (index > -1) {
                const s = sessions.value.splice(index, 1)[0];
                s.updated_at = new Date().toISOString();
                sessions.value.unshift(s);
            }

        } catch (e) {
            error.value = "Failed to send message.";
            // Remove optimistic message or show error?
            messages.value.push({
                id: Date.now(),
                role: 'system',
                content: "Error: Failed to send message. Please try again."
            });
        } finally {
            thinking.value = false;
        }
    }

    async function clearHistory() {
        try {
            const headers = await getAuthHeaders();
            await axios.delete(`${API_URL}/chat/sessions`, headers);
            sessions.value = [];
            const toast = useToast();
            toast.success("History cleared");
            messages.value = [];
            currentContext.value = []; // Clear context
            currentSession.value = null;
        } catch (e) {
            error.value = "Failed to clear history.";
            const toast = useToast();
            toast.error("Failed to clear history");
        }
    }

    async function sendFeedback(messageId, type) {
        try {
            const headers = await getAuthHeaders();
            await axios.post(`${API_URL}/chat/messages/${messageId}/feedback`, { feedback: type }, headers);
            // Optionally update local message state if we stored meta_info locally
        } catch (e) {
            console.error("Failed to send feedback", e);
            const toast = useToast();
            toast.error("Failed to submit feedback");
        }
    }

    return {
        sessions,
        currentSession,
        messages,
        isLoading,
        thinking,
        error,
        fetchSessions,
        createSession,
        selectSession,
        sendMessage,
        clearHistory,
        sendFeedback,
        selectedModel,
        availableModels,
        currentContext
    };
});
