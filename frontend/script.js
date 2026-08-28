let chatHistory = [];

async function sendMessage() {
    const inputElement = document.getElementById("user-input");
    const message = inputElement.value.trim();
    if (!message) return;

    const chatBox = document.getElementById("chat-box");
    const typingIndicator = document.getElementById("typing-indicator");
    const timeString = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    // 1. Add User Message Bubble
    const userWrapper = document.createElement("div");
    userWrapper.className = "message-wrapper user-wrapper";
    userWrapper.innerHTML = `
        <div class="avatar">👤</div>
        <div class="message-bubble user-bubble">
            <p>${escapeHtml(message)}</p>
            <span class="timestamp">${timeString}</span>
        </div>
    `;
    chatBox.appendChild(userWrapper);

    inputElement.value = "";
    chatBox.scrollTop = chatBox.scrollHeight;

    // 2. Show Typing Indicator
    typingIndicator.classList.remove("hidden");
    chatBox.scrollTop = chatBox.scrollHeight;

    try {
        const response = await fetch("http://127.0.0.1:5000/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                message: message,
                history: chatHistory
            })
        });

        const data = await response.json();
        const botTimeString = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

        // Hide Typing Indicator
        typingIndicator.classList.add("hidden");

        // 3. Add Bot Message Bubble
        const botWrapper = document.createElement("div");
        botWrapper.className = "message-wrapper bot-wrapper";
        botWrapper.innerHTML = `
            <div class="avatar">🤖</div>
            <div class="message-bubble bot-bubble">
                <p>${escapeHtml(data.response)}</p>
                <span class="timestamp">${botTimeString}</span>
            </div>
        `;
        chatBox.appendChild(botWrapper);

        // 4. Save to Memory History
        chatHistory.push({ role: "user", text: message });
        chatHistory.push({ role: "model", text: data.response });

    } catch (error) {
        console.error("Error:", error);
        typingIndicator.classList.add("hidden");
        const errorWrapper = document.createElement("div");
        errorWrapper.className = "message-wrapper bot-wrapper";
        errorWrapper.innerHTML = `
            <div class="avatar">🤖</div>
            <div class="message-bubble bot-bubble" style="background:#ffdddd; color:#d32f2f;">
                <p>❌ Could not connect to backend server.</p>
            </div>
        `;
        chatBox.appendChild(errorWrapper);
    }

    chatBox.scrollTop = chatBox.scrollHeight;
}

function toggleDarkMode() {
    document.body.classList.toggle("dark-mode");
}

function clearChat() {
    chatHistory = [];
    const chatBox = document.getElementById("chat-box");
    chatBox.innerHTML = `
        <div class="message-wrapper bot-wrapper">
            <div class="avatar">🤖</div>
            <div class="message-bubble bot-bubble">
                <p>Chat cleared! Memory reset. How can I help you?</p>
                <span class="timestamp">Just now</span>
            </div>
        </div>
    `;
}

document.addEventListener("DOMContentLoaded", () => {
    const inputElement = document.getElementById("user-input");
    if (inputElement) {
        inputElement.addEventListener("keypress", (event) => {
            if (event.key === "Enter") {
                sendMessage();
            }
        });
    }
});

function escapeHtml(text) {
    const div = document.createElement("div");
    div.innerText = text;
    return div.innerHTML;
}