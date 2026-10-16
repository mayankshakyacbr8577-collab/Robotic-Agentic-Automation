// DOM Elements
const chatForm = document.getElementById('chatForm');
const questionInput = document.getElementById('questionInput');
const chatMessages = document.getElementById('chatMessages');
const sendButton = document.getElementById('sendButton');
const buttonText = sendButton.querySelector('.button-text');
const loadingSpinner = sendButton.querySelector('.loading-spinner');

// API Configuration
const API_URL = '/api/chat';

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    questionInput.focus();
});

// Handle form submission
chatForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const question = questionInput.value.trim();
    
    if (!question) return;
    
    // Add user message to chat
    addMessage(question, 'user');
    
    // Clear input and disable button
    questionInput.value = '';
    setLoading(true);
    
    try {
        // Send question to API
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ question })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // Add bot response to chat
            addMessage(data.answer, 'bot');
        } else {
            // Show error message
            addMessage(`Error: ${data.error}`, 'bot');
        }
    } catch (error) {
        console.error('Error:', error);
        addMessage('Sorry, something went wrong. Please try again.', 'bot');
    } finally {
        setLoading(false);
        questionInput.focus();
    }
});

// Add message to chat
function addMessage(content, type) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    // Parse the content and format it
    const formattedContent = formatMessage(content);
    contentDiv.innerHTML = formattedContent;
    
    messageDiv.appendChild(contentDiv);
    chatMessages.appendChild(messageDiv);
    
    // Scroll to bottom
    scrollToBottom();
}

// Format message content (handle line breaks and lists)
function formatMessage(content) {
    // Convert line breaks to <br>
    let formatted = content.replace(/\n\n/g, '</p><p>');
    formatted = formatted.replace(/\n/g, '<br>');
    
    // Wrap in <p> tags
    formatted = `<p>${formatted}</p>`;
    
    // Convert bullet points
    formatted = formatted.replace(/• /g, '<li>');
    formatted = formatted.replace(/- /g, '<li>');
    
    // Wrap list items in <ul>
    formatted = formatted.replace(/(<li>.*<\/li>)/g, '<ul>$1</ul>');
    
    // Clean up multiple <ul> tags
    formatted = formatted.replace(/<\/ul><ul>/g, '');
    
    return formatted;
}

// Set loading state
function setLoading(isLoading) {
    sendButton.disabled = isLoading;
    
    if (isLoading) {
        buttonText.style.display = 'none';
        loadingSpinner.style.display = 'inline';
    } else {
        buttonText.style.display = 'inline';
        loadingSpinner.style.display = 'none';
    }
}

// Scroll chat to bottom
function scrollToBottom() {
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Handle Enter key (already handled by form submit, but this prevents double submission)
questionInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
    }
});
