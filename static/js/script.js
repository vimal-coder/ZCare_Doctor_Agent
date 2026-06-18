let currentSessionId = null;

// DOM Elements
const fileInput = document.getElementById('pdfFile');
const uploadZone = document.getElementById('uploadZone');
const statusDiv = document.getElementById('uploadStatus');

const extractedDataBox = document.getElementById('extractedData');
const chatInput = document.getElementById('chatInput');
const sendBtn = document.getElementById('sendBtn');
const uploadTitle = uploadZone.querySelector('.upload-title');
const uploadHint = uploadZone.querySelector('.upload-hint');

// Drag and Drop Events
uploadZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadZone.classList.add('dragover');
});

uploadZone.addEventListener('dragleave', (e) => {
    e.preventDefault();
    uploadZone.classList.remove('dragover');
});

uploadZone.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadZone.classList.remove('dragover');
    
    if (e.dataTransfer.files.length) {
        fileInput.files = e.dataTransfer.files;
        handleFileSelection();
    }
});

// File Input Event
fileInput.addEventListener('change', () => {
    if (fileInput.files.length > 0) {
        handleFileSelection();
    }
});

function handleFileSelection() {
    if (fileInput.files.length === 0) return;

    const files = Array.from(fileInput.files);
    
    // Check if all files are PDFs
    const allPdfs = files.every(file => file.type === "application/pdf" || file.name.toLowerCase().endsWith('.pdf'));
    
    if (!allPdfs) {
        statusDiv.innerHTML = "<span style='color: #ef4444; font-weight: 500;'>Only PDF reports are supported.</span>";
        fileInput.value = "";
        uploadTitle.innerText = "Drag & Drop PDF(s) Here";
        uploadHint.innerText = "Supported format: PDF (Max 50MB)";
        return;
    }

    if (files.length === 1) {
        uploadTitle.innerText = files[0].name;
    } else {
        uploadTitle.innerText = `${files.length} files selected`;
    }
    
    uploadHint.innerText = "Ready to analyze";
    // Auto trigger upload
    uploadReport();
}


// Function to handle the PDF upload
async function uploadReport() {
    if (fileInput.files.length === 0) return;

    const formData = new FormData();
    for (let i = 0; i < fileInput.files.length; i++) {
        formData.append("files", fileInput.files[i]);
    }

    statusDiv.innerHTML = "Processing documents and extracting clinical context...";
    statusDiv.style.color = "var(--text-muted)";

    try {
        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (response.ok) {
            currentSessionId = data.session_id;
            statusDiv.innerHTML = "<span style='color: var(--primary-green); font-weight: 500;'>Analysis complete!</span>";
            

            displayExtractedData(data.extracted_data);
            
            // Enable chat inputs
            chatInput.disabled = false;
            sendBtn.disabled = false;
            
            // Clear init message
            document.getElementById('chatWindow').innerHTML = '';
            
            addMessageToChat("system", "Reports analyzed successfully. How can I assist you with this patient?");
        } else {
            statusDiv.innerHTML = `<span style='color: #ef4444;'>Error: ${data.detail}</span>`;
        }
    } catch (error) {
        statusDiv.innerHTML = `<span style='color: #ef4444;'>Connection Error: ${error.message}</span>`;
    }
}

// Function to format and display the structured data on the left panel
function displayExtractedData(data) {
    const contextContent = document.getElementById('contextContent');
    
    let html = '';
    const formatList = (list) => list && list.length > 0 ? list.join(', ') : 'None noted';

    html += `<div class="data-group"><strong>Diagnoses:</strong> <span>${formatList(data.diagnoses)}</span></div>`;
    html += `<div class="data-group"><strong>Medications:</strong> <span>${formatList(data.medications)}</span></div>`;
    html += `<div class="data-group"><strong>Conditions:</strong> <span>${formatList(data.medical_conditions)}</span></div>`;
    html += `<div class="data-group"><strong>Allergies:</strong> <span>${formatList(data.allergies)}</span></div>`;
    html += `<div class="data-group"><strong>Lab Results:</strong> <span>${formatList(data.laboratory_results)}</span></div>`;

    contextContent.innerHTML = html;
    extractedDataBox.style.display = 'block';
}

// Quick action query handler
function setQuickQuery(query) {
    if (!currentSessionId) {
        alert("Please upload a medical report first.");
        return;
    }
    chatInput.value = query;
    sendMessage();
}

// Function to handle sending chat messages
async function sendMessage() {
    const message = chatInput.value.trim();

    if (!message || !currentSessionId) return;

    // Display user message
    addMessageToChat('user', message);
    chatInput.value = '';
    
    // Disable inputs while waiting for AI
    chatInput.disabled = true;
    sendBtn.disabled = true;

    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                session_id: currentSessionId,
                message: message
            })
        });

        const data = await response.json();

        if (response.ok) {
            addMessageToChat('ai', data.response);
        } else {
            addMessageToChat('system', `Error: ${data.detail}`);
        }
    } catch (error) {
        addMessageToChat('system', `Connection Error: ${error.message}`);
    } finally {
        chatInput.disabled = false;
        sendBtn.disabled = false;
        chatInput.focus();
    }
}

function getCurrentTime() {
    const now = new Date();
    let hours = now.getHours();
    let minutes = now.getMinutes();
    const ampm = hours >= 12 ? 'PM' : 'AM';
    hours = hours % 12;
    hours = hours ? hours : 12; // the hour '0' should be '12'
    minutes = minutes < 10 ? '0' + minutes : minutes;
    return hours + ':' + minutes + ' ' + ampm;
}

// Helper to append messages to the chat window
function addMessageToChat(role, text) {
    const chatWindow = document.getElementById('chatWindow');
    const messageDiv = document.createElement('div');
    const timeStr = getCurrentTime();
    
    // Format newlines into HTML breaks for AI responses
    const formattedText = text.replace(/\n/g, '<br>');
    
    if (role === 'user') {
        messageDiv.className = 'message-wrapper user';
        messageDiv.innerHTML = `
            <div class="message-header">You</div>
            <div class="message-content">${formattedText}</div>
            <div class="msg-footer">${timeStr} <i class="ph-bold ph-check"></i></div>
        `;
    } else if (role === 'ai') {
        messageDiv.className = 'message-wrapper ai';
        messageDiv.innerHTML = `
            <div class="message-header">
                <span class="ai-avatar"><i class="ph-fill ph-robot"></i></span> 
                AI Assistant
            </div>
            <div class="message-content">${formattedText}</div>
            <div class="msg-footer">${timeStr}</div>
        `;
    } else {
        // System message
        messageDiv.className = 'message-wrapper ai'; // Styling like AI but simpler
        messageDiv.innerHTML = `
            <div class="message-header" style="color: var(--text-muted);">System</div>
            <div class="message-content" style="background-color: #f1f5f9;">${formattedText}</div>
            <div class="msg-footer">${timeStr}</div>
        `;
    }
    
    chatWindow.appendChild(messageDiv);
    // Auto-scroll to bottom
    chatWindow.scrollTop = chatWindow.scrollHeight;
}

// Allow pressing "Enter" to send the message
chatInput.addEventListener('keypress', function (e) {
    if (e.key === 'Enter') {
        sendMessage();
    }
});

// Init system message
window.onload = () => {
    addMessageToChat("system", "Please upload a patient medical report (.pdf) to begin the analysis.");
};

// Clear all data and reset UI
async function clearAllData() {
    if (currentSessionId) {
        try {
            await fetch('/api/clear', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ session_id: currentSessionId })
            });
        } catch (error) {
            console.error("Failed to clear session on server:", error);
        }
    }

    // Reset state
    currentSessionId = null;

    // Reset Upload UI
    fileInput.value = "";
    uploadTitle.innerText = "Drag & Drop PDF(s) Here";
    uploadHint.innerText = "Supported format: PDF (Max 50MB)";
    statusDiv.innerHTML = "";
    extractedDataBox.style.display = 'none';
    document.getElementById('contextContent').innerHTML = "";

    // Reset Chat UI
    const chatWindow = document.getElementById('chatWindow');
    chatWindow.innerHTML = '';
    chatInput.value = '';
    chatInput.disabled = true;
    sendBtn.disabled = true;

    // Re-initialize system message
    addMessageToChat("system", "Please upload a patient medical report (.pdf) to begin the analysis.");
}