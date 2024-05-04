from flask import Flask, render_template, Response, request, redirect, url_for, flash, g, send_from_directory, abort
from camera import Webcam
import cv2
from object_detection import ObjectDetector
import os
from datetime import datetime
import face_recognition
import numpy as np
import sqlite3
from userauth import register_user, login_user, db
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv
import secrets

load_dotenv()  # Load environment variables from .env file

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Generate a random secret key using secrets.token_hex(16)
secret_key = secrets.token_hex(16)

# Set the secret key for your Flask application
app.secret_key = secret_key

db.init_app(app)

limiter = Limiter(app)

with app.app_context():
    db.create_all()

cam1 = Webcam(0)
cam2 = Webcam(1)

recording_status = False

matched_faces_folder = 'static/matched_faces'
object_images_folder = 'static/object_images'

recording = False  # Flag to indicate recording status
camera_feeds = {0: cam1, 1: cam2}

output_match_faces = 'static/matched_faces'
if not os.path.exists(output_match_faces):
    os.makedirs(output_match_faces)

output_folder = 'static/recordings'
if not os.path.exists(output_folder):
    os.makedirs(output_folder)
    
object_images = 'static/object_images'
if not os.path.exists(object_images):
    os.makedirs(object_images)

detector = ObjectDetector("models/yolov8n-seg.pt")
object_of_interest = ''

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        register_user(username, password)
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))

    # Handle GET request (render the registration form)
    return render_template('register.html')

@app.route('/login', methods=['GET','POST'])
@limiter.limit("5 per minute")  # Example rate limit: 5 requests per minute
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if login_user(username, password):
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password. Please try again.', 'danger')
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/logout')
def logout():
    # You can clear the session or perform any other logout-related actions here
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

known_face_encoding = None

def gen_frames(camera, camera_name):
    global known_face_encoding

    image_count = {'camera1': 0, 'camera2': 0}

    while True:
        frame = camera.get_frame()
        annotated_frame = detector.detect_objects(frame, object_of_interest, camera_name)

        if frame is not None:
            overlay_text(frame, camera)

            if known_face_encoding is not None:
                face_locations = face_recognition.face_locations(frame)
                face_encodings = face_recognition.face_encodings(frame, face_locations)

                for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
                    match = face_recognition.compare_faces([known_face_encoding], face_encoding)
                    label = "No Match"
                    cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
                    if match[0]:
                        label = "Match"
                        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                        if image_count[camera_name] < 3:
                            capture_image(frame, camera_name)
                            image_count[camera_name] += 1
                            print(f"Image captured from {camera_name}. Count: {image_count[camera_name]}")

                    cv2.putText(frame, label, (left + 6, bottom + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

            camera.write_frame(frame)

            ret, buffer = cv2.imencode('.jpg', frame)
            if ret:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
            else:
                print("Error encoding frame")

def capture_image(frame, camera_name):
    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"match_face_{camera_name}_{current_time}.jpg"
    filepath = os.path.join(output_match_faces, filename)
    cv2.imwrite(filepath, frame)
    print(f"Saved image from {camera_name}: {filename}")

def overlay_text(frame, camera):
    cv2.circle(frame, (30, 30), 10, (0, 0, 255), -1)
    cv2.putText(frame, "LIVE", (30 + 15, 30 + 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cv2.putText(frame, current_time, (frame.shape[1] - 250, frame.shape[0] - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

    camera_name = f"Camera {camera.cam_id}"
    cv2.putText(frame, camera_name, (frame.shape[1] - 150, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

@app.route('/upload_image', methods=['POST'])
def upload_image():
    global known_face_encoding

    try:
        if 'image' in request.files:
            uploaded_image = request.files['image']
            image_data = uploaded_image.read()
            image_np = np.frombuffer(image_data, dtype=np.uint8)
            image_cv2 = cv2.imdecode(image_np, cv2.IMREAD_COLOR)

            uploaded_face_encoding = face_recognition.face_encodings(image_cv2)
            if len(uploaded_face_encoding) > 0:
                known_face_encoding = uploaded_face_encoding[0]
                return 'Image uploaded and processed successfully.'
            else:
                return 'No face found in the uploaded image.'
        else:
            return 'No image uploaded.'
    except Exception as e:
        return f'Error processing image: {e}'

@app.route('/video_feed1')
def video_feed1():
    return Response(gen_frames(cam1, 'camera1'), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/video_feed2')
def video_feed2():
    return Response(gen_frames(cam2, 'camera2'), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/set_object', methods=['POST'])
def set_object():
    global object_of_interest
    object_of_interest = request.form['object_of_interest']
    detector.reset_image_count()

    for _ in range(3):
        frame1 = cam1.get_frame()
        annotated_frame1 = detector.detect_objects(frame1, object_of_interest, 'camera1')
        
        frame2 = cam2.get_frame()
        annotated_frame2 = detector.detect_objects(frame2, object_of_interest, 'camera2')

    return '', 204

@app.route('/start_recording/<int:cam_id>')
def start_recording(cam_id):
    if cam_id in camera_feeds:
        camera_feeds[cam_id].start_recording()
        return 'Recording started.'
    else:
        return 'Camera not found.', 404

@app.route('/stop_recording/<int:cam_id>')
def stop_recording(cam_id):
    if cam_id in camera_feeds:
        camera_feeds[cam_id].stop_recording()
        return 'Recording stopped and saved.'
    else:
        return 'Camera not found.', 404

# Route to start recording for all cameras
@app.route('/start_recording_all')
def start_recording_all():
    global recording
    if not recording:
        for cam_id, camera in camera_feeds.items():
            camera.start_recording()
        recording = True
        return 'Recording started for all cameras.'
    else:
        return 'Recording is already in progress.'
    
# Route to stop recording for all cameras
@app.route('/stop_recording_all')
def stop_recording_all():
    global recording
    if recording:
        for cam_id, camera in camera_feeds.items():
            camera.stop_recording()
        recording = False
        return 'Recording stopped and saved for all cameras.'
    else:
        return 'No recording is currently in progress.'

@app.route('/recordings/<path:filename>')
def download_file(filename):
    return send_from_directory(output_folder, filename, as_attachment=True)

@app.route('/turn_off_face_recognition')
def turn_off_face_recognition():
    global known_face_encoding
    known_face_encoding = None
    return 'Face recognition turned off.'

@app.route('/turn_off_object_detection')
def turn_off_object_detection():
    global object_of_interest
    object_of_interest = '' 
    detector.reset_image_count()
    return 'Object detection turned off.'

@app.route('/get_object_images')
def get_object_images():
    object_images = os.listdir('static/object_images')
    return {'images': object_images}

@app.route('/get_matched_faces')
def get_matched_faces():
    matched_faces = os.listdir('static/matched_faces')
    return {'images': matched_faces}

@app.route('/get_recorded_videos')
def get_recorded_videos():
    recorded_videos = os.listdir('static/recordings')
    return {'videos': recorded_videos, 'recording_status': recording_status}

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(error):
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(debug=True)



