// static/js/components/dashboardStore.js
document.addEventListener('alpine:init', () => {
    // Configure marked with highlight.js
    if (typeof marked !== 'undefined' && typeof hljs !== 'undefined') {
        marked.setOptions({
            highlight: function(code, lang) {
                if (lang && hljs.getLanguage(lang)) {
                    try {
                        return hljs.highlight(code, { language: lang }).value;
                    } catch (e) {}
                }
                return hljs.highlightAuto(code).value;
            },
            breaks: true,
            gfm: true
        });
    }

    Alpine.data('dashboardStore', () => ({
        conversations: [],
        currentConversation: { id: null, name: '', messages: [] },
        projects: [],
        isProjectReady: false,
        messages: [],
        currentMessage: '',
        isLoading: false,

        init() {
            this.loadConversations();
            this.loadProjects();
            if (this.conversations.length === 0) {
                this.newConversation();
            } else {
                this.switchConversation(this.conversations[0].id);
            }
            // Auto‑scroll after the DOM is ready
            this.$nextTick(() => {
                this.scrollToBottom();
            });
        },

        renderMarkdown(content) {
            if (!content) return '';
            try {
                return marked.parse(content);
            } catch (e) {
                return content;
            }
        },

        loadConversations() {
            const stored = localStorage.getItem('codeforge_conversations');
            if (stored) {
                this.conversations = JSON.parse(stored);
            } else {
                this.conversations = [
                    { id: Date.now(), name: 'New Chat', updated_at: new Date().toISOString() }
                ];
                this.saveConversations();
            }
        },

        saveConversations() {
            localStorage.setItem('codeforge_conversations', JSON.stringify(this.conversations));
        },

        newConversation() {
            const conv = {
                id: Date.now(),
                name: 'New Chat',
                updated_at: new Date().toISOString()
            };
            this.conversations.unshift(conv);
            this.saveConversations();
            this.switchConversation(conv.id);
        },

        switchConversation(id) {
            const found = this.conversations.find(c => c.id === id);
            if (found) {
                this.currentConversation = found;
                this.loadMessagesForCurrent();
                // Scroll to bottom after messages load
                this.$nextTick(() => {
                    this.scrollToBottom();
                });
            }
        },

        loadMessagesForCurrent() {
            if (this.currentConversation && this.currentConversation.id) {
                const key = `codeforge_messages_${this.currentConversation.id}`;
                const stored = localStorage.getItem(key);
                this.messages = stored ? JSON.parse(stored) : [];
            } else {
                this.messages = [];
            }
        },

        saveMessages() {
            if (this.currentConversation && this.currentConversation.id) {
                const key = `codeforge_messages_${this.currentConversation.id}`;
                localStorage.setItem(key, JSON.stringify(this.messages));
            }
        },

        async loadProjects() {
            try {
                const response = await fetch('/api/projects/');
                if (response.ok) {
                    const data = await response.json();
                    this.projects = data;
                } else {
                    this.projects = [];
                }
            } catch (e) {
                this.projects = [];
            }
        },

        openProject(id) {
            window.location.href = `/studio/${id}/`;
        },

        generateProject() {
            alert('Project generation will be available after you discuss your stack in chat.');
        },

        async sendMessage() {
            if (!this.currentMessage.trim() || this.isLoading) return;
            const msg = this.currentMessage.trim();
            this.messages.push({ role: 'user', content: msg, id: Date.now() });
            this.saveMessages();
            this.currentMessage = '';
            this.isLoading = true;

            const assistantMsgId = Date.now() + 1;
            this.messages.push({ role: 'assistant', content: '', id: assistantMsgId });
            this.scrollToBottom();

            try {
                const response = await fetch('/chat/stream/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')?.value || '',
                    },
                    body: JSON.stringify({ message: msg, conversation_id: this.currentConversation.id }),
                });

                const reader = response.body.getReader();
                const decoder = new TextDecoder();
                let buffer = '';
                while (true) {
                    const { done, value } = await reader.read();
                    if (done) break;
                    buffer += decoder.decode(value, { stream: true });
                    const assistantMsg = this.messages.find(m => m.id === assistantMsgId);
                    if (assistantMsg) {
                        assistantMsg.content = buffer;
                        this.saveMessages();
                        this.scrollToBottom();
                    }
                }
            } catch (error) {
                const assistantMsg = this.messages.find(m => m.id === assistantMsgId);
                if (assistantMsg) {
                    assistantMsg.content = '⚠️ Error: ' + error.message;
                    this.saveMessages();
                }
            } finally {
                this.isLoading = false;
                this.scrollToBottom();
            }
        },

        scrollToBottom() {
            this.$nextTick(() => {
                const container = this.$refs.messages;
                if (container) {
                    container.scrollTop = container.scrollHeight;
                }
            });
        }
    }));
});