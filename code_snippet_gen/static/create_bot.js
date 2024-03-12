document.addEventListener("DOMContentLoaded", function() {
    const modelTypeInputs = document.querySelectorAll('input[name="modelType"]');
    modelTypeInputs.forEach(input => {
        input.addEventListener('change', function() {
            document.getElementById("apiKeySection").style.display = input.value === "remote" ? "block" : "none";
        });
    });
});

document.getElementById("proceedButton").onclick = async function(event) {
    event.preventDefault(); // Prevent the default button click behavior

    const modelType = document.querySelector('input[name="modelType"]:checked').value;
    let apiKey = "";
    
    if (modelType === "remote") {
        apiKey = document.getElementById("apiKeyInput").value;
        if (!apiKey) {
            document.getElementById("message").innerText = "Please enter your API key.";
            return;
        }
    }

    const baseUrl = window.location.origin;
    const response = await fetch(`${baseUrl}/create_bot/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ key: apiKey })
    });

    if (response.ok) {
        const result = await response.json();
        if (result.status === "ok") {
            window.location.href = "chat.html"; // Redirect to the chat page
        } else {
            document.getElementById("message").innerText = result.msg || "Error processing your request. Please try again.";
        }
    } else {
        document.getElementById("message").innerText = "An error occurred. Please try again.";
    }
};
