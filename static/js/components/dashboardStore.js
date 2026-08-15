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
        messages: [],
        currentMessage: '',
        isLoading: false,

        init() {
            this.loadConversations();
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
        },

        deleteConversation(convId) {

            window.modal.openConfirm(
                'Delete Conversation',
                'Delete this conversation permanently?',
                () => {
                    // 1. Remove from the conversations array
                    const index = this.conversations.findIndex(c => c.id === convId);
                    if (index === -1) return;
                    this.conversations.splice(index, 1);
                    this.saveConversations();

                    // 2. Delete messages from localStorage
                    const key = `codeforge_messages_${convId}`;
                    localStorage.removeItem(key);

                    // 3. If the current conversation was deleted, switch to another one
                    if (this.currentConversation.id === convId) {
                        if (this.conversations.length > 0) {
                            this.switchConversation(this.conversations[0].id);
                        } else {
                            // No conversations left – create a new one
                            this.newConversation();
                        }
                    }
                }
            );
        },
        
        copyCode(content) {
            // Extract all code blocks from the markdown content
            const codeBlockRegex = /```(?:\w+)?\n([\s\S]*?)```/g;
            let allCode = '';
            let match;
            while ((match = codeBlockRegex.exec(content)) !== null) {
                allCode += match[1] + '\n\n';
            }
            if (allCode.trim()) {
                navigator.clipboard.writeText(allCode.trim());
                if (window.toast) {
                    window.toast.show('Code copied to clipboard!', 'success');
                } else {
                    window.toast.show('✅ Code copied to clipboard!', 'success');
                }
            } else {
                // Fallback: copy the entire message
                navigator.clipboard.writeText(content);
                if (window.toast) {
                    window.toast.show('Text copied to clipboard!', 'success');
                }
            }
        },

        exportChat() {
            if (!this.messages.length) {
                window.toast.show('No messages to export.' , 'error');
                return;
            }
            // Build a markdown string
            let md = `# CodeForge Chat Export\n\n**Exported on:** ${new Date().toLocaleString()}\n\n`;
            this.messages.forEach(msg => {
                const role = msg.role === 'user' ? 'You' : 'CodeForge';
                md += `## ${role}\n\n`;
                md += msg.content + '\n\n';
            });
            // Create a download link
            const blob = new Blob([md], { type: 'text/markdown' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `codeforge-chat-${Date.now()}.md`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        }
        
    }));
});