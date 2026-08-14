// apps/studio/static/studio/studio.js

document.addEventListener('alpine:init', () => {
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

    Alpine.data('studioDetail', () => ({
        projectId: window.projectId,
        tree: [],
        messages: [],
        currentMessage: '',
        isLoading: false,
        previewContent: 'Select a file to preview',
        selectedModel: '1.5B',

        // ---------- Init ----------
        init() {
            this.loadFileTree();
            this.loadChatHistory();
            this.loadModelPreference();
        },

        // ---------- Markdown ----------
        renderMarkdown(content) {
            if (!content) return '';
            try {
                return marked.parse(content);
            } catch (e) {
                return content;
            }
        },

        // ---------- File Tree ----------
        async loadFileTree() {
            try {
                const response = await fetch(`/studio/${this.projectId}/files/`);
                const data = await response.json();
                this.tree = data.tree || [];
                this.tree = this.addExpandedState(this.tree);
            } catch (e) {
                console.error('Failed to load file tree:', e);
                this.tree = [];
            }
        },

        addExpandedState(items, depth = 0) {
            return items.map(item => {
                if (item.is_dir) {
                    item.expanded = depth === 0; // Expand only root folders
                    if (item.children && item.children.length > 0) {
                        item.children = this.addExpandedState(item.children, depth + 1);
                    } else {
                        item.children = [];
                    }
                }
                return item;
            });
        },

        toggleFolder(item) {
            if (item.is_dir) {
                item.expanded = !item.expanded;
                this.tree = [...this.tree];
            }
        },

        async selectFile(path) {
            this.previewContent = 'Loading...';
            try {
                const response = await fetch(`/studio/${this.projectId}/file/?path=${encodeURIComponent(path)}`);
                const data = await response.json();
                this.previewContent = data.content || 'File is empty.';
                if (typeof hljs !== 'undefined') {
                    const previewEl = document.querySelector('.preview-content');
                    if (previewEl) {
                        hljs.highlightElement(previewEl);
                    }
                }
            } catch (e) {
                this.previewContent = 'Error loading file.';
            }
        },

        // ---------- Chat History ----------
        async loadChatHistory() {
            try {
                const response = await fetch(`/studio/${this.projectId}/chat/history/`);
                if (response.ok) {
                    const data = await response.json();
                    this.messages = data;
                    // Auto‑scroll to bottom after loading
                    this.$nextTick(() => {
                        this.scrollToBottom();
                    });
                } else {
                    this.messages = [];
                }
            } catch (e) {
                console.error('Failed to load chat history:', e);
                this.messages = [];
            }
        },

        // ---------- Model Preference ----------
        async loadModelPreference() {
            try {
                const response = await fetch('/studio/api/get-model/');
                if (response.ok) {
                    const data = await response.json();
                    this.selectedModel = data.model_type || '1.5B';
                } else {
                    this.selectedModel = '1.5B';
                }
            } catch (e) {
                console.error('Failed to load model preference:', e);
                this.selectedModel = '1.5B';
            }
        },

        async switchModel(modelType) {
            try {
                const response = await fetch('/studio/api/set-model/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')?.value || '',
                    },
                    body: JSON.stringify({ model_type: modelType }),
                });
                if (response.ok) {
                    // Optional: show a toast notification
                    window.toast.show('Model switched to ' + modelType, 'success');
                } else {
                    window.toast.show('Failed to switch model.', 'error');
                }
            } catch (e) {
                console.error('Failed to switch model:', e);
                window.toast.show('Error switching model.', 'error');
            }
        },

        // ---------- Send Message ----------
        async sendMessage() {
            if (!this.currentMessage.trim() || this.isLoading) return;
            const msg = this.currentMessage.trim();
            this.messages.push({ role: 'user', content: msg, id: Date.now() });
            this.currentMessage = '';
            this.isLoading = true;

            const assistantId = Date.now() + 1;
            this.messages.push({ role: 'assistant', content: '', id: assistantId });
            this.scrollToBottom();

            try {
                const response = await fetch(`/studio/${this.projectId}/chat/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')?.value || '',
                    },
                    body: JSON.stringify({ message: msg }),
                });

                const reader = response.body.getReader();
                const decoder = new TextDecoder();
                let buffer = '';
                while (true) {
                    const { done, value } = await reader.read();
                    if (done) break;
                    buffer += decoder.decode(value, { stream: true });
                    const assistantMsg = this.messages.find(m => m.id === assistantId);
                    if (assistantMsg) {
                        assistantMsg.content = buffer;
                        this.scrollToBottom();
                    }
                }
                this.loadFileTree();
                this.loadChatHistory();
            } catch (error) {
                const assistantMsg = this.messages.find(m => m.id === assistantId);
                if (assistantMsg) {
                    assistantMsg.content = '⚠️ Error: ' + error.message;
                }
            } finally {
                this.isLoading = false;
                this.scrollToBottom();
            }
        },

        scrollToBottom() {
            this.$nextTick(() => {
                const container = document.querySelector('.studio-chat .chat-messages-container');
                if (container) container.scrollTop = container.scrollHeight;
            });
        }
    }));
});