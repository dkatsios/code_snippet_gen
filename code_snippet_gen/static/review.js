window.onload = () => {
    const codeSnippetArea = document.getElementById('codeSnippet');
    const snippet = localStorage.getItem("reviewSnippetCode");
    codeSnippetArea.value = snippet || "";
};

document.getElementById("runButton").onclick = async () => {
    const index = localStorage.getItem("reviewSnippetIndex");
    const code = document.getElementById('codeSnippet').value;
    const response = await fetch('/execute/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ index: index, code: code })
    });

    if (response.ok) {
        const result = await response.json();
        document.querySelector('#resultArea pre').textContent = result.output;
    } else {
        console.error('Failed to execute the snippet.');
    }
};
