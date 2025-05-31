// DOM Elements
const uploadArea = document.getElementById('upload-area');
const fileInput = document.getElementById('file-input');
const uploadContent = document.querySelector('.upload-content');
const previewContainer = document.getElementById('preview-container');
const previewImage = document.getElementById('preview-image');
const removeBtn = document.getElementById('remove-btn');
const translateBtn = document.getElementById('translate-btn');
const sourceLang = document.getElementById('source-lang');
const targetLang = document.getElementById('target-lang');

// Section Elements
const uploadSection = document.querySelector('.upload-section');
const progressSection = document.getElementById('progress-section');
const resultSection = document.getElementById('result-section');
const errorSection = document.getElementById('error-section');

// Progress Elements
const progressBar = document.getElementById('progress-bar');
const progressText = document.getElementById('progress-text');
const steps = document.querySelectorAll('.step');

// Result Elements
const resultImage = document.getElementById('result-image');
const downloadBtn = document.getElementById('download-btn');
const newTranslationBtn = document.getElementById('new-translation-btn');

// Error Elements
const errorMessage = document.getElementById('error-message');
const retryBtn = document.getElementById('retry-btn');

// State
let currentFile = null;
let currentJobId = null;

// File Upload Handlers
uploadArea.addEventListener('click', () => fileInput.click());
fileInput.addEventListener('change', handleFileSelect);
uploadArea.addEventListener('dragover', handleDragOver);
uploadArea.addEventListener('dragleave', handleDragLeave);
uploadArea.addEventListener('drop', handleDrop);
removeBtn.addEventListener('click', removeFile);
translateBtn.addEventListener('click', startTranslation);
downloadBtn.addEventListener('click', downloadResult);
newTranslationBtn.addEventListener('click', resetApp);
retryBtn.addEventListener('click', resetApp);

function handleFileSelect(e) {
    const file = e.target.files[0];
    if (file && validateFile(file)) {
        currentFile = file;
        displayPreview(file);
    }
}

function handleDragOver(e) {
    e.preventDefault();
    uploadArea.classList.add('dragover');
}

function handleDragLeave(e) {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
}

function handleDrop(e) {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
    
    const file = e.dataTransfer.files[0];
    if (file && validateFile(file)) {
        currentFile = file;
        displayPreview(file);
    }
}

function validateFile(file) {
    const validTypes = ['image/png', 'image/jpeg', 'image/jpg', 'image/gif', 'image/webp'];
    const isImage = validTypes.includes(file.type);
    const isPDF = file.name.toLowerCase().endsWith('.pdf');
    
    if (!isImage && !isPDF) {
        showError('Please upload a valid image or PDF file');
        return false;
    }
    
    if (file.size > 16 * 1024 * 1024) {
        showError('File size must be less than 16MB');
        return false;
    }
    
    return true;
}

function displayPreview(file) {
    const reader = new FileReader();
    reader.onload = (e) => {
        if (file.type.startsWith('image/')) {
            previewImage.src = e.target.result;
        } else if (file.name.toLowerCase().endsWith('.pdf')) {
            // Show PDF icon for PDF files
            previewImage.src = 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAzODQgNTEyIj48cGF0aCBmaWxsPSIjNjY2IiBkPSJNMzY0LjIgODMuOUwyODguMSA3LjhDMjgyLjYgMi44IDI3NS4yIDAgMjY3LjUgMEg2NEM0Ni4zIDAgMzIgMTQuMyAzMiAzMnY0NDhjMCAxNy43IDE0LjMgMzIgMzIgMzJoMjg4YzE3LjcgMCAzMi0xNC4zIDMyLTMyVjk2LjVjMC03LjctMi44LTE1LjEtNy44LTIwLjZ6TTI4OCAzNDRjMCAxMy4zLTEwLjcgMjQtMjQgMjRzLTI0LTEwLjctMjQtMjRWMTkyYzAtMTMuMyAxMC43LTI0IDI0LTI0czI0IDEwLjcgMjQgMjR2MTUyek0xOTIgMzQ0YzAgMTMuMy0xMC43IDI0LTI0IDI0cy0yNC0xMC43LTI0LTI0VjE5MmMwLTEzLjMgMTAuNy0yNCAyNC0yNHMyNCAxMC43IDI0IDI0djE1MnpNOTYgMzQ0YzAgMTMuMy0xMC43IDI0LTI0IDI0cy0yNC0xMC43LTI0LTI0VjE5MmMwLTEzLjMgMTAuNy0yNCAyNC0yNHMyNCAxMC43IDI0IDI0djE1MnoiLz48L3N2Zz4=';
        }
        uploadContent.style.display = 'none';
        previewContainer.style.display = 'block';
        translateBtn.disabled = false;
    };
    reader.readAsDataURL(file);
}

function removeFile() {
    currentFile = null;
    fileInput.value = '';
    previewImage.src = '';
    uploadContent.style.display = 'block';
    previewContainer.style.display = 'none';
    translateBtn.disabled = true;
}

async function startTranslation() {
    if (!currentFile) return;
    
    const formData = new FormData();
    formData.append('file', currentFile);
    formData.append('source_lang', sourceLang.value);
    formData.append('target_lang', targetLang.value);
    
    try {
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (response.ok) {
            currentJobId = data.job_id;
            showProgressSection();
            pollStatus();
        } else {
            showError(data.error || 'Failed to start translation');
        }
    } catch (error) {
        showError('Network error. Please try again.');
    }
}

function showProgressSection() {
    uploadSection.style.display = 'none';
    progressSection.style.display = 'block';
    resultSection.style.display = 'none';
    errorSection.style.display = 'none';
    
    // Reset progress
    progressBar.style.width = '0%';
    steps.forEach(step => step.classList.remove('active'));
    steps[0].classList.add('active');
}

async function pollStatus() {
    if (!currentJobId) return;
    
    try {
        const response = await fetch(`/status/${currentJobId}`);
        const data = await response.json();
        
        if (response.ok) {
            updateProgress(data.progress);
            
            if (data.status === 'completed') {
                showResult(data.is_pdf, data.all_pages);
            } else if (data.status === 'failed') {
                showError(data.error || 'Translation failed');
            } else {
                // Continue polling
                setTimeout(pollStatus, 1000);
            }
        } else {
            showError('Failed to get status');
        }
    } catch (error) {
        showError('Network error while checking status');
    }
}

function updateProgress(progress) {
    progressBar.style.width = `${progress}%`;
    
    // Update steps and text based on progress
    if (progress >= 10) {
        steps[0].classList.add('active');
        progressText.textContent = 'Detecting speech bubbles...';
    }
    if (progress >= 30) {
        steps[1].classList.add('active');
        progressText.textContent = 'Extracting text from bubbles...';
    }
    if (progress >= 60) {
        steps[2].classList.add('active');
        progressText.textContent = 'Translating text...';
    }
    if (progress >= 90) {
        steps[3].classList.add('active');
        progressText.textContent = 'Applying translated text...';
    }
}

function showResult(isPdf, allPages) {
    uploadSection.style.display = 'none';
    progressSection.style.display = 'none';
    resultSection.style.display = 'block';
    errorSection.style.display = 'none';
    
    // Set result image
    resultImage.src = `/download/${currentJobId}`;
    
    // Update download button text for PDFs
    if (isPdf) {
        downloadBtn.innerHTML = '<i class="fas fa-download"></i> Download All Pages';
        downloadBtn.onclick = () => {
            window.location.href = `/download/all/${currentJobId}`;
        };
    } else {
        downloadBtn.innerHTML = '<i class="fas fa-download"></i> Download Translated Comic';
        downloadBtn.onclick = downloadResult;
    }
}

function showError(message) {
    uploadSection.style.display = 'none';
    progressSection.style.display = 'none';
    resultSection.style.display = 'none';
    errorSection.style.display = 'block';
    
    errorMessage.textContent = message;
}

async function downloadResult() {
    if (!currentJobId) return;
    
    try {
        const response = await fetch(`/download/${currentJobId}`);
        const blob = await response.blob();
        
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `translated_comic_${currentJobId}.png`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
    } catch (error) {
        showError('Failed to download file');
    }
}

function resetApp() {
    currentFile = null;
    currentJobId = null;
    fileInput.value = '';
    
    uploadSection.style.display = 'block';
    progressSection.style.display = 'none';
    resultSection.style.display = 'none';
    errorSection.style.display = 'none';
    
    removeFile();
} 