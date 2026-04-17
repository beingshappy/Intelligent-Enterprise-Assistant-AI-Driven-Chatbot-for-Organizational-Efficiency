class ChatEngine {
    constructor() {
        this.chatBox = document.getElementById('chat-messages');
        this.input = document.getElementById('chat-input');
        this.indicator = document.getElementById('typing-indicator');
        this.isTyping = false;
    }

    async loadHistory() {
        try {
            const history = await auth.fetchWithAuth('/chat/history');
            
            // Only clear welcome message if there is actual history to show
            if (history && history.length > 0) {
                this.chatBox.innerHTML = ''; 
                history.forEach(msg => {
                    this.appendMessage(msg.content, msg.is_user ? 'user' : 'bot');
                });
                this.scrollToBottom();
            }
        } catch (err) {
            console.error("Failed to load history", err);
        }
    }

    appendMessage(content, type) {
        const div = document.createElement('div');
        div.className = `msg ${type}-msg`;
        div.innerHTML = `<div class="msg-content">${this.formatContent(content)}</div>`;
        this.chatBox.appendChild(div);
        this.scrollToBottom();
    }

    formatContent(content) {
        // Basic markdown-like formatting for better presentation
        return content
            .replace(/\n/g, '<br>')
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>');
    }

    showTyping(show, statusText = "AI is thinking...") {
        if (show) {
            // Re-append to ensure it's always the absolute last element
            this.chatBox.appendChild(this.indicator);
            this.indicator.classList.remove('hidden');
            const textEl = document.getElementById('typing-text');
            if (textEl) textEl.innerText = statusText;
        } else {
            this.indicator.classList.add('hidden');
        }
        this.scrollToBottom();
    }

    scrollToBottom() {
        this.chatBox.scrollTo({
            top: this.chatBox.scrollHeight,
            behavior: 'smooth'
        });
    }

    async sendMessage() {
        const message = this.input.value.trim();
        if (!message || this.isTyping) return;

        this.appendMessage(message, 'user');
        this.input.value = '';
        this.isTyping = true;
        this.showTyping(true, "Searching Knowledge Base...");

        try {
            // Simulated state update for better demo feel
            setTimeout(() => {
                if(this.isTyping) this.showTyping(true, "Analyzing Context...");
            }, 5000);

            const data = await auth.fetchWithAuth('/chat/', {
                method: 'POST',
                body: JSON.stringify({ message })
            });
            
            this.showTyping(false);
            this.isTyping = false;
            
            if (data.response) {
                this.appendMessage(data.response, 'bot');
            } else {
                this.appendMessage(data.detail || "I'm having trouble connecting to the server.", 'bot');
            }
        } catch (err) {
            this.showTyping(false);
            this.isTyping = false;
            this.appendMessage("Network error. Please check your connection.", 'bot');
        }
    }
}

const chatEngine = new ChatEngine();

window.sendMessage = () => chatEngine.sendMessage();

// Handle Enter key
document.getElementById('chat-input')?.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') chatEngine.sendMessage();
});
