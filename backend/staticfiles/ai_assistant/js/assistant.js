/**
 * MediNest AI Health Assistant JavaScript
 * Handles CSRF token extraction, message rendering, POST fetch requests,
 * typing indicators, auto-scrolling, and clearing conversation.
 */

document.addEventListener("DOMContentLoaded", function () {
    const chatForm = document.getElementById("chatForm");
    const userInput = document.getElementById("userInput");
    const sendBtn = document.getElementById("sendBtn");
    const chatBox = document.getElementById("chatBox");
    const clearChatBtn = document.getElementById("clearChatBtn");
    const suggestionPills = document.querySelectorAll(".suggestion-pill");

    if (!chatForm || !userInput || !chatBox) {
        return;
    }

    // Helper: Extract CSRF Token from Cookie or Input
    function getCsrfToken() {
        const csrfInput = document.querySelector("[name=csrfmiddlewaretoken]");
        if (csrfInput && csrfInput.value) {
            return csrfInput.value;
        }
        let cookieValue = null;
        if (document.cookie && document.cookie !== "") {
            const cookies = document.cookie.split(";");
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, 10) === "csrftoken=") {
                    cookieValue = decodeURIComponent(cookie.substring(10));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // Helper: Scroll Chat to Bottom
    function scrollToBottom() {
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    // Helper: Escape HTML to prevent XSS attacks
    function escapeHtml(str) {
        const div = document.createElement("div");
        div.appendChild(document.createTextNode(str));
        return div.innerHTML;
    }

    // Helper: Format message text safely with line breaks & bold formatting
    function formatMessageText(str) {
        if (!str) return "";
        let escaped = escapeHtml(str);
        escaped = escaped.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
        escaped = escaped.replace(/\*(.*?)\*/g, "<em>$1</em>");
        escaped = escaped.replace(/\n/g, "<br>");
        return escaped;
    }

    // Helper: Append User Message to Chat UI
    function appendUserMessage(text) {
        const messageRow = document.createElement("div");
        messageRow.className = "message-row user-row";
        messageRow.innerHTML = `
            <div class="avatar-icon user-avatar">
                <i class="fa-solid fa-user"></i>
            </div>
            <div class="message-bubble user-bubble">${formatMessageText(text)}</div>
        `;
        chatBox.appendChild(messageRow);
        scrollToBottom();
    }

    // Helper: Append AI Message to Chat UI
    function appendAiMessage(text, isError = false) {
        const messageRow = document.createElement("div");
        messageRow.className = "message-row ai-row";
        
        const bubbleClass = isError ? "message-bubble ai-bubble border-danger text-danger" : "message-bubble ai-bubble";
        
        messageRow.innerHTML = `
            <div class="avatar-icon ai-avatar">
                <i class="fa-solid fa-user-doctor"></i>
            </div>
            <div class="${bubbleClass}">${formatMessageText(text)}</div>
        `;
        chatBox.appendChild(messageRow);
        scrollToBottom();
    }

    // Helper: Show Typing Indicator
    function showTypingIndicator() {
        const indicatorRow = document.createElement("div");
        indicatorRow.id = "typingIndicator";
        indicatorRow.className = "message-row ai-row";
        indicatorRow.innerHTML = `
            <div class="avatar-icon ai-avatar">
                <i class="fa-solid fa-user-doctor"></i>
            </div>
            <div class="message-bubble ai-bubble">
                <div class="typing-indicator">
                    <span class="typing-dot"></span>
                    <span class="typing-dot"></span>
                    <span class="typing-dot"></span>
                </div>
            </div>
        `;
        chatBox.appendChild(indicatorRow);
        scrollToBottom();
    }

    // Helper: Hide Typing Indicator
    function hideTypingIndicator() {
        const indicator = document.getElementById("typingIndicator");
        if (indicator) {
            indicator.remove();
        }
    }

    // Submit Message Handler
    async function sendMessage(messageText) {
        const text = messageText ? messageText.trim() : userInput.value.trim();
        if (!text) {
            return;
        }

        // Disable UI controls
        userInput.value = "";
        userInput.disabled = true;
        sendBtn.disabled = true;

        // Display user message
        appendUserMessage(text);

        // Show loading indicator
        showTypingIndicator();

        try {
            const csrfToken = getCsrfToken();
            const response = await fetch("/ai-assistant/api/chat/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": csrfToken || "",
                },
                body: JSON.stringify({ message: text }),
            });

            hideTypingIndicator();

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                const errorMsg = errorData.error || "Sorry, the AI assistant is temporarily unavailable. Please try again later.";
                appendAiMessage(errorMsg, true);
            } else {
                const data = await response.json();
                if (data.success) {
                    appendAiMessage(data.response);
                } else {
                    appendAiMessage(data.error || "An error occurred while processing your request.", true);
                }
            }
        } catch (err) {
            hideTypingIndicator();
            appendAiMessage("Network error. Please check your internet connection and try again.", true);
        } finally {
            // Re-enable UI controls
            userInput.disabled = false;
            sendBtn.disabled = false;
            userInput.focus();
            scrollToBottom();
        }
    }

    // Form submit event
    chatForm.addEventListener("submit", function (e) {
        e.preventDefault();
        sendMessage();
    });

    // Suggestion pills click handler
    suggestionPills.forEach((pill) => {
        pill.addEventListener("click", function () {
            const query = this.getAttribute("data-query") || this.innerText;
            if (query) {
                sendMessage(query);
            }
        });
    });

    // Clear conversation handler
    if (clearChatBtn) {
        clearChatBtn.addEventListener("click", function () {
            // Reset chat box content to initial state
            chatBox.innerHTML = `
                <div class="message-row ai-row">
                    <div class="avatar-icon ai-avatar">
                        <i class="fa-solid fa-user-doctor"></i>
                    </div>
                    <div class="message-bubble ai-bubble">
                        Hello! I am your <strong>MediNest AI Health Assistant</strong>.<br><br>
                        I can provide general health and wellness information, answer health questions, and offer educational guidance.<br><br>
                        <em>How can I assist you with your health and wellness today?</em>
                    </div>
                </div>
            `;
            scrollToBottom();
        });
    }

    // Auto-scroll on initial load
    scrollToBottom();
});
