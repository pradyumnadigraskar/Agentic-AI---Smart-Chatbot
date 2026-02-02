async function uploadPDF() {
    const fileInput = document.getElementById('pdfInput');
    const statusDiv = document.getElementById('uploadStatus');
    const file = fileInput.files[0];

    if (!file) {
        statusDiv.innerHTML = "<span style='color: #e74c3c;'>Please select a file first.</span>";
        return;
    }

    const formData = new FormData();
    formData.append("file", file);

    statusDiv.innerHTML = "<span style='color: #f1c40f;'>Uploading & Indexing...</span>";

    try {
        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        if (response.ok) {
            statusDiv.innerHTML = `<span style='color: #2ecc71;'>Success! Indexed ${result.chunks_indexed} chunks.</span>`;
        } else {
            statusDiv.innerHTML = `<span style='color: #e74c3c;'>Error: ${result.detail}</span>`;
        }
    } catch (error) {
        statusDiv.innerHTML = `<span style='color: #e74c3c;'>Network Error</span>`;
        console.error('Error:', error);
    }
}

function handleEnter(event) {
    if (event.key === 'Enter') {
        sendMessage();
    }
}

async function sendMessage() {
    const inputField = document.getElementById('userQuery');
    const query = inputField.value.trim();

    if (!query) return;

    // 1. Add User Message
    appendMessage(query, 'user');
    inputField.value = '';

    // 2. Add "Thinking..." Message
    const botMsgId = appendMessage('<i class="fas fa-spinner fa-spin"></i> Thinking...', 'bot');
    const botMsgDiv = document.getElementById(botMsgId);
    
    let isFirstChunk = true;
    let fullText = "";

    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ query: query })
        });

        const reader = response.body.getReader();
        const decoder = new TextDecoder();

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            const chunk = decoder.decode(value, { stream: true });
            
            // --- FIX: Clear "Thinking..." immediately on the very first chunk ---
            if (isFirstChunk) {
                botMsgDiv.innerHTML = ""; 
                isFirstChunk = false;
            }
            // ------------------------------------------------------------------

            // Check for Eval Data
            if (chunk.includes("__EVAL_START__")) {
                const parts = chunk.split("__EVAL_START__");
                const textPart = parts[0];
                const evalPart = parts[1] ? parts[1].split("__EVAL_END__")[0] : null;
                
                // Append remaining text if any
                if (textPart) {
                    fullText += textPart;
                    botMsgDiv.innerHTML = formatText(fullText); 
                }
                
                // Render Evaluation Box
                if (evalPart) {
                    try {
                        const evalData = JSON.parse(evalPart);
                        const evalHtml = `
                            <div class="eval-box">
                                <strong>Score:</strong> ${evalData.score}/10 | 
                                <strong>Feedback:</strong> ${evalData.feedback}
                            </div>`;
                        botMsgDiv.insertAdjacentHTML('beforeend', evalHtml);
                    } catch (e) { console.error("Eval parse error", e); }
                }
                
            } else {
                // Normal Text Stream
                fullText += chunk;
                botMsgDiv.innerHTML = formatText(fullText);
            }
            
            // Auto scroll to bottom
            const chatHistory = document.getElementById('chatHistory');
            chatHistory.scrollTop = chatHistory.scrollHeight;
        }

    } catch (error) {
        botMsgDiv.innerHTML = "Error connecting to server.";
        console.error('Error:', error);
    }
}

// Helper to format basic markdown from LLM
function formatText(text) {
    // 1. Replace newlines with <br>
    let formatted = text.replace(/\n/g, '<br>');
    
    // 2. Replace **bold** with <b>bold</b>
    formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<b>$1</b>');
    
    // 3. Handle bullet points (lines starting with * or -)
    // This simple regex wraps lines starting with * in a span for slight styling
    formatted = formatted.replace(/(?:^|<br>)[*-] (.*?)(?=<br>|$)/g, '<br>• $1');

    return formatted;
}

function appendMessage(htmlContent, sender) {
    const chatHistory = document.getElementById('chatHistory');
    const msgDiv = document.createElement('div');
    const id = 'msg-' + Date.now();
    
    msgDiv.id = id;
    msgDiv.classList.add('message');
    msgDiv.classList.add(sender === 'user' ? 'user-message' : 'bot-message');
    msgDiv.innerHTML = htmlContent;
    
    chatHistory.appendChild(msgDiv);
    chatHistory.scrollTop = chatHistory.scrollHeight;
    
    return id;
}