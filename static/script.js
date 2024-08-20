function startRegistration() {
    const name = document.getElementById('name').value;
    if (!name) {
        alert('Please enter a name.');
        return;
    }

    const video = document.getElementById('video');
    const canvas = document.getElementById('canvas');
    const context = canvas.getContext('2d');

    navigator.mediaDevices.getUserMedia({ video: true })
        .then(stream => {
            video.srcObject = stream;
            video.play();

            setTimeout(() => {
                canvas.width = video.videoWidth;
                canvas.height = video.videoHeight;
                context.drawImage(video, 0, 0);
                const imageData = canvas.toDataURL('image/jpeg');

                fetch('/register_face', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        name: name,
                        image: imageData.split(',')[1]
                    })
                })
                .then(response => response.json())
                .then(data => {
                    document.getElementById('status').innerText = data.message;
                    video.srcObject.getTracks().forEach(track => track.stop());
                });
            }, 3000); 
        })
        .catch(error => console.error('Error accessing camera:', error));
}

function startRecognition() {
    const video = document.getElementById('video');
    const canvas = document.getElementById('canvas');
    const context = canvas.getContext('2d');

    navigator.mediaDevices.getUserMedia({ video: true })
        .then(stream => {
            video.srcObject = stream;
            video.play();

            function recognizeFace() {
                canvas.width = video.videoWidth;
                canvas.height = video.videoHeight;
                context.drawImage(video, 0, 0);
                const imageData = canvas.toDataURL('image/jpeg');

                fetch('/recognize', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ image: imageData.split(',')[1] })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.names.length > 0) {
                        document.getElementById('result').innerText = 'Recognized: ' + data.names.join(', ');
                    } else {
                        document.getElementById('result').innerText = 'No faces recognized';
                    }
                });

                setTimeout(recognizeFace, 3000); 
            }

            recognizeFace();
        })
        .catch(error => console.error('Error accessing camera:', error));
}

function deleteEmployee(name) {
    fetch('/delete_employee', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: name })
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message);
        location.reload();
    });
}

function searchEmployees() {
    const query = document.getElementById('search').value.toLowerCase();
    const list = document.getElementById('employeeList');
    const items = list.getElementsByTagName('li');

    for (let i = 0; i < items.length; i++) {
        const name = items[i].textContent.toLowerCase();
        if (name.includes(query)) {
            items[i].style.display = '';
        } else {
            items[i].style.display = 'none';
        }
    }
}


function fetchLogs() {
    fetch('/get_logs')
        .then(response => response.json())
        .then(data => {
            const logsContainer = document.getElementById('logs');
            logsContainer.innerHTML = data.logs.join('<br>');
        });
}


function fetchAttendance() {
    fetch('/get_attendance')
        .then(response => response.json())
        .then(data => {
            const attendanceContainer = document.getElementById('attendance');
            attendanceContainer.innerHTML = data.logs.join('<br>');
        });
}

window.onload = function() {
    if (document.getElementById('logs')) {
        fetchLogs();
    }
    if (document.getElementById('attendance')) {
        fetchAttendance();
    }
}


