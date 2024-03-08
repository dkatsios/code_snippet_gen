function delay(time) {
    return new Promise(resolve => setTimeout(resolve, time));
  }
  
document.getElementById("apiKeyForm").onsubmit = async function(event) {
    event.preventDefault(); // Prevent the default form submission behavior

    const apiKey = document.getElementById("apiKeyInput").value;
    console.log("apiKey", apiKey)
    const baseUrl = window.location.origin;
    const response = await fetch(`${baseUrl}/set_key/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ key: apiKey })
    });

    if (response.ok) {
        console.log("set_key response ok")
        await delay(2000);
        const result = await response.json();
        if (result) {
            // Proceed to the next step if the API key is valid
            console.log("set_key result true")
            await delay(2000);
            window.location.href = "chat.html"; // Redirect to the next step page
        } else {
            // Stay on the same page and show an error message
            console.log("set_key result false")
            await delay(2000);
            document.getElementById("message").innerText = "The API key is not valid. Please try again.";
        }
    } else {
        // Handle HTTP errors
        console.log("set_key response error")
        await delay(2000);
        document.getElementById("message").innerText = "An error occurred. Please try again.";
    }
};
