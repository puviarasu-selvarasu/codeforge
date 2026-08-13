// static/js/components/chatWidget.js (updated)
document.addEventListener('alpine:init', () => {
    Alpine.data('chatWidget', (options = {}) => {
        return {
            conversationId: options.conversationId || null,
            messages: [],
            currentMessage: '',
            isLoading: false,
            initMessages() {
                // Load messages from localStorage if any
                if (this.conversationId) {
                    const key = `codeforge_messages_${this.conversationId}`;
                    const stored = localStorage.getItem(key);
                    if (stored) {
                        this.messages = JSON.parse(stored);
                    } else {
                        this.messages = [];
                    }
                }
                // Listen for load-messages event from dashboardStore
                window.addEventListener('load-messages', (e) => {
                    if (e.detail && e.detail.messages) {
                        this.messages = e.detail.messages;
                    }
                });
                this.scrollToBottom();
            },
            saveMessages() {
                if (this.conversationId) {
                    const key = `codeforge_messages_${this.conversationId}`;
                    localStorage.setItem(key, JSON.stringify(this.messages));
                }
            },
            scrollToBottom() {
                this.$nextTick(() => {
                    const container = this.$refs.messages;
                    if (container) container.scrollTop = container.scrollHeight;
                });
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
                        body: JSON.stringify({ message: msg, conversation_id: this.conversationId }),
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
                }
            }
        };
    });
});