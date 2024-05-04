# camera.py
import cv2
import time

class Webcam:
    def __init__(self, cam_id):
        self.cam_id = cam_id
        self.camera = cv2.VideoCapture(cam_id)
        self.recording = False
        self.timestamp = time.strftime("%Y%m%d_%H%M%S")
        self.output_path = f"static/recordings/camera_{self.cam_id}_{self.timestamp}.mp4"
        self.codec = cv2.VideoWriter_fourcc(*'mp4v')  # MP4 codec
        self.out = None  # Initialize out attribute

    def get_frame(self):
        ret, frame = self.camera.read()
        if not ret:
            raise ValueError("Failed to get frame from webcam")
        return frame

    def start_recording(self):
        if not self.recording:
            self.recording = True
            self.timestamp = time.strftime("%Y%m%d_%H%M%S")  # Current date and time for filename
            self.output_path = f"static/recordings/camera_{self.cam_id}_{self.timestamp}.mp4"
            self.out = cv2.VideoWriter(self.output_path, self.codec, 20.0, (640, 480))

    def stop_recording(self):
        if self.recording:
            self.recording = False
            self.out.release()
            self.out = None  # Reset out attribute after releasing

    def write_frame(self, frame):
        if self.recording and self.out is not None:  # Check if out is initialized
            self.out.write(frame)

    def release(self):
        if self.recording:
            self.stop_recording()
        self.camera.release()






