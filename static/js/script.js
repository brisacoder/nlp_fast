document.getElementById('uploadForm').addEventListener('submit', function(e) {
    e.preventDefault();
    const formData = new FormData(this);
    fetch('/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (response.ok) {
            return response.json();
        } else {
            throw new Error('Upload failed');
        }
    })
    .then(data => {
        alert(data.message);
    })
    .catch(error => {
        alert('Error: ' + error.message);
    });
});

document.getElementById('questionForm').addEventListener('submit', function(e) {
    e.preventDefault();
    const question = document.getElementById('question').value;
    if (!question.trim()) {
        alert('Please enter a question');
        return;
    }
    fetch('/ask', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
            'question': question
        })
    })
    .then(response => {
        if (response.ok) {
            return response.json();
        } else {
            throw new Error('Question failed');
        }
    })
    .then(data => {
        document.getElementById('response').value = data.response;
    })
    .catch(error => {
        alert('Error: ' + error.message);
    });
});

function clearBoxes() {
    document.getElementById('question').value = '';
    document.getElementById('response').value = '';
}
