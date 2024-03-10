async function loadChatHistory() {
    const baseUrl = window.location.origin;
    const response = await fetch(`${baseUrl}/chat_messages/`);

    if (response.ok) {
        const messages = await response.json();
        messages.forEach((message, index) => {
            // Determine who the sender is based on the message's position in the array
            const sender = index % 2 === 0 ? 'User' : 'Bot';
            displayMessage(message, sender);
        });
    } else {
        console.error('Failed to load chat history.');
        // You might want to handle this error more gracefully
    }
}

async function checkBot() {
    const baseUrl = window.location.origin;
    const response = await fetch(`${baseUrl}/check_bot/`);

    if (response.ok) {
        const data = await response.json();
        if (data.status === "error") {
            window.location.href = '/static/create_bot.html';
        } else {
            // Load the chat history if the bot status is OK
            await loadChatHistory();
        }
    } else {
        console.error('Failed to check the bot status.');
    }
}

checkBot();

function displayMessage(message, sender) {
    const chatArea = document.getElementById('chatArea');
    const messageElement = document.createElement('div');
    const pre = document.createElement('pre');
    const code = document.createElement('code');

    code.textContent = message;
    pre.appendChild(code);
    messageElement.appendChild(pre);

    messageElement.style.marginBottom = '10px';

    if (sender === 'User') {
        messageElement.style.textAlign = 'right';
        messageElement.style.fontWeight = 'bold';
    } else {
        messageElement.style.textAlign = 'left';
        pre.style.backgroundColor = '#f1f1f1';
        pre.style.padding = '5px';
        pre.style.borderRadius = '5px';
    }

    chatArea.appendChild(messageElement);
    chatArea.scrollTop = chatArea.scrollHeight; // Scroll to the bottom
}

async function sendMessage() {
    const userInput = document.getElementById('userInput');
    const userText = userInput.value;

    if (userText.trim() === '') {
        return; // Don't send empty messages
    }

    displayMessage(userText, 'User');
    userInput.value = ''; // Clear the input field

    const baseUrl = window.location.origin;
    const response = await fetch(`${baseUrl}/prompt/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ user_input: userText })
    });

    if (response.ok) {
        const data = await response.json();
        if (data.successful) {
            displayMessage(data.msg, 'Bot');
        } else {
            displayMessage('Failed to get a response from the bot.', 'Bot');
        }
    } else {
        displayMessage('Failed to send message. Please try again.', 'Bot');
    }
}

document.getElementById('userInput').addEventListener('keypress', function(event) {
    if (event.key === 'Enter') {
        event.preventDefault();
        sendMessage();
    }
});
