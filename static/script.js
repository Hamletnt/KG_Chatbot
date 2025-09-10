let conversationId = null;
let isStreaming = false;

function handleKeyPress(event) {
    if (event.key === 'Enter' && !isStreaming) {
        sendMessage();
    }
}

async function sendMessage() {
    const messageInput = document.getElementById('messageInput');
    const message = messageInput.value.trim();
    
    if (!message || isStreaming) return;
    
    // Disable input and show loading
    setLoading(true);
    messageInput.value = '';
    
    // Add user message to chat
    addMessage(message, 'user');
    
    try {
        // Create bot message placeholder
        const botMessageId = addStreamingMessage();
        
        // Send message to streaming API
        const response = await fetch('/api/v1/chat/stream', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message,
                conversation_id: conversationId
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        // Handle streaming response
        await handleStreamingResponse(response, botMessageId);
        
    } catch (error) {
        console.error('Error sending message:', error);
        addMessage('Sorry, I encountered an error. Please try again.', 'bot');
    } finally {
        setLoading(false);
    }
}

async function handleStreamingResponse(response, messageId) {
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';
    let currentContent = '';
    
    isStreaming = true;
    
    try {
        while (true) {
            const { value, done } = await reader.read();
            
            if (done) break;
            
            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split('\n');
            
            // Keep the last potentially incomplete line in buffer
            buffer = lines.pop() || '';
            
            for (const line of lines) {
                if (line.startsWith('data: ')) {
                    try {
                        const data = JSON.parse(line.slice(6));
                        
                        if (data.type === 'start') {
                            conversationId = data.conversation_id;
                            // Just update the conversation ID, message placeholder already exists
                            
                        } else if (data.type === 'token') {
                            currentContent += data.content;
                            updateStreamingMessage(messageId, currentContent, false);
                            conversationId = data.conversation_id;
                            
                            // Auto-scroll as content appears
                            const chatMessages = document.getElementById('chatMessages');
                            chatMessages.scrollTop = chatMessages.scrollHeight;
                            
                        } else if (data.type === 'final') {
                            updateStreamingMessage(messageId, data.content, true);
                            conversationId = data.conversation_id;
                        } else if (data.type === 'error') {
                            updateStreamingMessage(messageId, data.content, true);
                            conversationId = data.conversation_id;
                        }
                    } catch (e) {
                        console.error('Error parsing SSE data:', e);
                    }
                }
            }
        }
    } finally {
        isStreaming = false;
    }
}

function addStreamingMessage() {
    const chatMessages = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    const messageId = 'msg-' + Date.now();
    
    messageDiv.id = messageId;
    messageDiv.className = 'message bot-message';
    
    const now = new Date();
    const timeString = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    
    messageDiv.innerHTML = `
        <div class="message-content">
            <strong>Bot:</strong> 
            <span class="streaming-content"></span>
            <span class="typing-indicator">●</span>
        </div>
        <div class="message-time">${timeString}</div>
    `;
    
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    
    return messageId;
}

function updateStreamingMessage(messageId, content, isComplete) {
    const messageElement = document.getElementById(messageId);
    if (!messageElement) return;
    
    const contentSpan = messageElement.querySelector('.streaming-content');
    const typingIndicator = messageElement.querySelector('.typing-indicator');
    
    if (contentSpan) {
        contentSpan.textContent = content;
    }
    
    if (isComplete && typingIndicator) {
        typingIndicator.remove();
        // Add completion animation
        contentSpan.style.animation = 'none';
    }
    
    // Smooth scroll to bottom
    const chatMessages = document.getElementById('chatMessages');
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function addMessage(content, sender) {
    const chatMessages = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}-message`;
    
    const now = new Date();
    const timeString = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    
    messageDiv.innerHTML = `
        <div class="message-content">
            <strong>${sender === 'user' ? 'You' : 'Bot'}:</strong> ${content}
        </div>
        <div class="message-time">${timeString}</div>
    `;
    
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function setLoading(loading) {
    const messageInput = document.getElementById('messageInput');
    const sendButton = document.querySelector('.chat-input .btn');
    const sendButtonText = document.getElementById('sendButtonText');
    const sendButtonSpinner = document.getElementById('sendButtonSpinner');
    
    if (loading || isStreaming) {
        messageInput.disabled = true;
        sendButton.disabled = true;
        sendButtonText.classList.add('d-none');
        sendButtonSpinner.classList.remove('d-none');
    } else {
        messageInput.disabled = false;
        sendButton.disabled = false;
        sendButtonText.classList.remove('d-none');
        sendButtonSpinner.classList.add('d-none');
        messageInput.focus();
    }
}

// Focus on input when page loads
document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('messageInput').focus();
    
    // Check API health on load
    checkHealth();
});

async function checkHealth() {
    try {
        const response = await fetch('/api/v1/health');
        const data = await response.json();
        
        if (data.status !== 'healthy') {
            addMessage('Warning: Some services may not be fully available. Neo4j: ' + 
                      (data.neo4j_connected ? 'Connected' : 'Disconnected') + 
                      ', Azure OpenAI: ' + 
                      (data.azure_openai_configured ? 'Configured' : 'Not configured'), 'bot');
        }
    } catch (error) {
        console.error('Health check failed:', error);
        addMessage('Warning: Unable to verify service health.', 'bot');
    }
}
