document.getElementById("apiKeyForm").onsubmit = async function(event) {
    event.preventDefault(); // Prevent the default form submission behavior

    const apiKey = document.getElementById("apiKeyInput").value;
    console.log("apiKey", apiKey)
    const response = await fetch('http://localhost:5000/set_key/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ key: apiKey })
    });

    if (response.ok) {
        const result = await response.json();
        if (result) {
            // Proceed to the next step if the API key is valid
            window.location.href = "/next_step.html"; // Redirect to the next step page
        } else {
            // Stay on the same page and show an error message
            document.getElementById("message").innerText = "The API key is not valid. Please try again.";
        }
    } else {
        // Handle HTTP errors
        document.getElementById("message").innerText = "An error occurred. Please try again.";
    }
};
