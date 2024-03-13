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

document.getElementById('codeSnippet').addEventListener('keydown', function(e) {
    if (e.key === 'Tab') {
        e.preventDefault();  // Prevent the default tab behavior (focus change)
        var start = this.selectionStart;
        var end = this.selectionEnd;

        // Insert 4 spaces on TAB, remove 4 spaces on Shift+TAB
        if (!e.shiftKey) {
            // Set textarea value to: text before caret + 4 spaces + text after caret
            this.value = this.value.substring(0, start) + "    " + this.value.substring(end);

            // Move the caret to the end of the inserted spaces
            this.selectionStart = this.selectionEnd = start + 4;
        } else {
            // If the Shift key is also pressed, remove 4 spaces
            var beforeCaret = this.value.substring(0, start);
            
            // Check if the last 4 characters are spaces and if so, remove them
            if (beforeCaret.endsWith("    ")) {
                this.value = this.value.substring(0, start - 4) + this.value.substring(start);
                // Move the caret to the start position minus 4 (after removing the spaces)
                this.selectionStart = this.selectionEnd = start - 4;
            } else {
                // If there are not 4 spaces, just move the caret back one position
                this.selectionStart = this.selectionEnd = Math.max(start - 1, 0);
            }
        }
    }
});
