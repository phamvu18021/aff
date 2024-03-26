async function copyText(ev) {
    // Get the text field
    const activeId = ev.id;
    const copyText = document.getElementById(`input_${activeId}`);
    const buttons = document.querySelectorAll('.button-addon')

    if (navigator.clipboard && window.isSecureContext) {
        navigator.clipboard.writeText(copyText.value);
        copyText.select();
        copyText.setSelectionRange(0, 99999);

        for (let btn of buttons) {
            btn.classList.remove('active')
            btn.innerText = 'Copy'
        }
        ev.classList.add('active')
        ev.innerText = 'Copied'

    } else if (document.queryCommandSupported && document.queryCommandSupported("copy")) {
        var textarea = document.createElement("textarea");
        textarea.textContent = copyText.value;
        textarea.style.position = "fixed";  // Prevent scrolling to bottom of page in Microsoft Edge.
        document.body.appendChild(textarea);
        textarea.select();

        for (let btn of buttons) {
            btn.classList.remove('active')
            btn.innerText = 'Copy'
        }
        ev.classList.add('active')
        ev.innerText = 'Copied'

        try {
            return document.execCommand("copy");  // Security exception may be thrown by some browsers.
        } catch (ex) {
            console.warn("Copy to clipboard failed.", ex);
            return prompt("Copy to clipboard: Ctrl+C, Enter", text);
        } finally {
            document.body.removeChild(textarea);
        }
    }
}
