function delay(time) {
    return new Promise(resolve => setTimeout(resolve, time));
}

document.getElementById("apiKeyForm").onsubmit = async function(event) {
    event.preventDefault(); // Prevent the default form submission behavior

    const apiKey = document.getElementById("apiKeyInput").value;
    console.log("apiKey", apiKey);
    const baseUrl = window.location.origin;
    const response = await fetch(`${baseUrl}/create_bot/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ key: apiKey })
    });

    if (response.ok) {
        console.log("create_bot response ok");
        const result = await response.json();
        
        // Check the status from the response
        if (result.status === "ok") {
            // Proceed to the next step if the API key is valid
            console.log("API key validated successfully");
            window.location.href = "chat.html"; // Redirect to the chat page
        } else {
            // Stay on the same page and show an error message
            console.log("create_bot result false", result.msg);
            document.getElementById("message").innerText = result.msg || "The API key is not valid. Please try again.";
        }
    } else {
        // Handle HTTP errors
        console.log("create_bot response error");
        document.getElementById("message").innerText = "An error occurred. Please try again.";
    }
};
