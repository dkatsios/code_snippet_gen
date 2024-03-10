let selectedIndex = null;

window.onload = async () => {
    const historyArea = document.getElementById('historyArea');
    const response = await fetch('/history/');
    if (response.ok) {
        const history = await response.json();
        history.forEach((snippet, index) => {
            const div = document.createElement('div');
            div.className = 'snippet';
            div.innerHTML = `<pre><code>${escapeHtml(snippet)}</code></pre>`;
            div.onclick = () => selectSnippet(index, snippet);
            historyArea.appendChild(div);
        });
        
    } else {
        historyArea.textContent = 'Failed to load history.';
    }
};

function selectSnippet(index) {
    const snippets = document.querySelectorAll('.snippet');
    snippets.forEach(div => div.classList.remove('selected'));
    snippets[index].classList.add('selected');
    selectedIndex = index;
    document.getElementById('deleteButton').disabled = false;
}

document.getElementById('deleteButton').onclick = async () => {
    const baseUrl = window.location.origin;
    if (selectedIndex !== null) {
        const response = await fetch(`${baseUrl}/delete-snippet/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ index: selectedIndex }),
        });

        if (response.ok) {
            window.location.reload();
        } else {
            alert('Failed to delete the snippet.');
        }
    }
};


function escapeHtml(unsafeText) {
    return unsafeText
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}
