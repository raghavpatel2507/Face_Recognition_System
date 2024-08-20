from flask import Flask, request, render_template, jsonify, session, redirect, url_for
import face_recognition
import numpy as np
import os
import base64
from io import BytesIO
from PIL import Image
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = '987456213$#%^&*()CVDFasdf'

REGISTERED_FACES = 'registered_faces'
ATTENDANCE_LOG = 'attendance_log.txt'
LOG_FILE = 'face_recognition_log.txt'

# Ensure the folders exist
os.makedirs(REGISTERED_FACES, exist_ok=True)

# Store known face encodings and names
known_face_encodings = []
known_face_names = {}

def load_known_faces():
    global known_face_encodings, known_face_names
    known_face_encodings = []
    known_face_names = {}
    for filename in os.listdir(REGISTERED_FACES):
        if filename.endswith('.jpg'):
            name = os.path.splitext(filename)[0]
            img = face_recognition.load_image_file(os.path.join(REGISTERED_FACES, filename))
            encoding = face_recognition.face_encodings(img)
            if encoding:  # Ensure encoding is found
                known_face_encodings.append(encoding[0])
                known_face_names[len(known_face_encodings) - 1] = name

load_known_faces()

def log_recognition(name):
    with open(LOG_FILE, 'a') as log_file:
        log_file.write(f"{datetime.now()} - Recognized: {name}\n")

def log_attendance(name):
    with open(ATTENDANCE_LOG, 'a') as log_file:
        log_file.write(f"{datetime.now()} - Attendance: {name}\n")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/employee_list')
def employee_list():
    employees = [os.path.splitext(f)[0] for f in os.listdir(REGISTERED_FACES) if f.endswith('.jpg')]
    return render_template('employee_list.html', employees=employees)

@app.route('/dashboard')
def dashboard():
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html')

@app.route('/report')
def report():
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    return render_template('report.html')

@app.route('/register_face', methods=['POST'])
def register_face():
    data = request.json
    name = data['name']
    image_data = base64.b64decode(data['image'])
    image = Image.open(BytesIO(image_data))
    image_path = os.path.join(REGISTERED_FACES, f"{name}.jpg")
    image.save(image_path)

    load_known_faces()
    return jsonify({'message': 'Registration completed'})

@app.route('/recognize', methods=['POST'])
def recognize():
    data = request.json
    image_data = base64.b64decode(data['image'])
    image = Image.open(BytesIO(image_data))
    img = np.array(image)
    face_encodings = face_recognition.face_encodings(img)

    if not face_encodings:
        return jsonify({'names': ['No faces found in the image.']})

    face_names = []
    for face_encoding in face_encodings:
        distances = face_recognition.face_distance(known_face_encodings, face_encoding)
        best_match_index = np.argmin(distances)
        if distances[best_match_index] < 0.5:  
            name = known_face_names.get(best_match_index, "Unknown")
        else:
            name = "Unknown"
        face_names.append(name)
        log_recognition(name)
        if name != "Unknown":
            log_attendance(name)

    return jsonify({'names': face_names})

@app.route('/delete_employee', methods=['POST'])
def delete_employee():
    name = request.json['name']
    image_path = os.path.join(REGISTERED_FACES, f"{name}.jpg")
    if os.path.exists(image_path):
        os.remove(image_path)
        load_known_faces()
        return jsonify({'message': f'{name} has been deleted.'})
    return jsonify({'message': 'Employee not found.'})

@app.route('/get_logs')
def get_logs():
    with open(LOG_FILE, 'r') as log_file:
        logs = log_file.readlines()
    return jsonify({'logs': logs})

@app.route('/get_attendance')
def get_attendance():
    with open(ATTENDANCE_LOG, 'r') as log_file:
        logs = log_file.readlines()
    return jsonify({'logs': logs})

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Replace with real authentication
        if username == 'admin' and password == 'admin':
            session['logged_in'] = True
            return redirect(url_for('dashboard'))
        else:
            return 'Invalid credentials'
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)




