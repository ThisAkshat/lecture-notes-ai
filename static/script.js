// Custom JavaScript for large file handling
async function uploadAudio() {
    const fileInput = document.getElementById('audioFile');
    const file = fileInput.files[0];
    
    if (!file) {
        alert('Please select an audio file');
        return;
    }
    
    // Size warning for large files
    const fileSizeMB = file.size / (1024 * 1024);
    if (fileSizeMB > 50) {
        const confirmUpload = confirm(
            `This file is ${fileSizeMB.toFixed(1)} MB. ` +
            `Processing may take 3-8 minutes. Continue?`
        );
        if (!confirmUpload) return;
    }
    
    const formData = new FormData();
    formData.append('audio', file);
    
    const loadingDiv = document.getElementById('loading');
    loadingDiv.style.display = 'block';
    loadingDiv.innerHTML = `Processing ${fileSizeMB.toFixed(1)} MB file... This may take a few minutes.`;
    
    try {
        const response = await fetch('/process', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (result.error) {
            alert('Error: ' + result.error);
        } else {
            document.getElementById('transcript').value = result.transcript;
            document.getElementById('summary').value = result.summary;
            
            // Display quiz
            let quizHTML = '';
            result.quiz.forEach(q => {
                quizHTML += `<p><b>${q.question}</b><br>Answer: ${q.answer}</p>`;
            });
            document.getElementById('quiz').innerHTML = quizHTML;
        }
    } catch (error) {
        alert('Error: ' + error.message);
    }
    
    loadingDiv.style.display = 'none';
}