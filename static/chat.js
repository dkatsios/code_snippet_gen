function displayMessage(message, sender) {
    const chatArea = document.getElementById('chatArea');
    const messageElement = document.createElement('div');

    // Use pre and code tags for preformatted text
    const pre = document.createElement('pre');
    const code = document.createElement('code');

    // For added security, consider sanitizing 'message' to avoid XSS attacks
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

    // Display user message in the chat area
    displayMessage(userText, 'User');

    // Clear the input field
    userInput.value = '';

    // Send the user message to the backend and await the bot's response
    const baseUrl = window.location.origin;
    const response = await fetch(`${baseUrl}/prompt/`, {

        method: 'GET',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ user_input: userText })
    });

    if (response.ok) {
        const data = await response.json();
        // Display bot's response in the chat area
        if (data.successful) {
            displayMessage(data.msg, 'Bot');
        } else {
            displayMessage('Failed to get a response from the bot.', 'Bot');
        }
    } else {
        displayMessage('Failed to send message. Please try again.', 'Bot');
    }
}

async function checkBot() {
    try {
        const response = await fetch('http://localhost:8000/check_bot/');
        if (response.ok) {
            const data = await response.json();
            if (data.status !== 'ok') {
                window.location.href = 'static/set_key.html'; // Redirect if bot not instantiated
            }
            // Proceed if bot is instantiated
        } else {
            alert('Failed to check bot status. Please try again.');
            window.location.href = 'static/set_key.html'; // Redirect on failure to communicate
        }
    } catch (error) {
        console.error('Error checking bot status:', error);
        window.location.href = 'static/set_key.html'; // Redirect on exception
    }
}

// Call checkBot on page load
document.addEventListener('DOMContentLoaded', (event) => {
    checkBot();
});


document.getElementById('userInput').addEventListener('keypress', function(event) {
    if (event.key === 'Enter') {
        event.preventDefault(); // Prevent default Enter key behavior (new line or form submission)
        sendMessage();
    }
});
