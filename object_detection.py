# object_detection.py
import cv2
import os
import time
from ultralytics import YOLO
import supervision as sv



class ObjectDetector:
    def __init__(self, model_path):
        self.model = YOLO(model_path)
        self.box_annotator = sv.BoxAnnotator(
            thickness=2,
            text_thickness=2,
            text_scale=1
        )

        self.image_count_cam1 = 0
        self.image_count_cam2 = 0
        self.max_images = 3  # Set the maximum number of images to capture


    def detect_objects(self, frame, object_of_interest, camera_id):
        result = self.model(frame, agnostic_nms=True)[0]
        detections = sv.Detections.from_yolov8(result)
        detections_filtered = [
            (box, confidence, class_id, self.model.model.names[class_id])
            for box, confidence, class_id, _
            in detections
            if class_id >= 0 and self.model.model.names[class_id].lower() == object_of_interest.lower() and confidence > 0.6
        ]
        labels_ = [detection[3] for detection in detections_filtered]
        annotated_frame = self.box_annotator.annotate(
            scene=frame,
            detections=detections_filtered,
            labels = labels_
        )

        if detections_filtered:
            # Save the frame when object is detected and image count is less than the maximum
            if camera_id == 'camera1' and self.image_count_cam1 < self.max_images:
                self.save_image(annotated_frame, object_of_interest, camera_id)
            elif camera_id == 'camera2' and self.image_count_cam2 < self.max_images:
                self.save_image(annotated_frame, object_of_interest, camera_id)

        return annotated_frame

    def save_image(self, frame, object_name, camera_id):
        current_time = time.strftime("%Y%m%d_%H%M%S")
        filename = f"{object_name}_{camera_id}_{current_time}.jpg"
        filepath = os.path.join('static/object_images', filename)
        cv2.imwrite(filepath, frame)
        print(f"Saved {object_name} image from Camera {camera_id}: {filename}")

        # Update image count based on camera ID
        if camera_id == 'camera1':
            self.image_count_cam1 += 1
        elif camera_id == 'camera2':
            self.image_count_cam2 += 1

    def reset_image_count(self):
        self.image_count_cam1 = 0
        self.image_count_cam2 = 0





