import cv2
import numpy as np
import requests
import urllib.request
import mediapipe as mp
import time
from urllib.error import URLError

class ESP32CameraProcessor:
    def __init__(self, esp32_url, mediapipe_solution="hands"):
        """
        Initialize the ESP32 camera processor with MediaPipe integration
        
        Args:
            esp32_url (str): The URL of the ESP32 camera stream
            mediapipe_solution (str): The MediaPipe solution to use ('hands', 'face', 'pose', 'holistic')
        """
        self.esp32_url = esp32_url
        self.mediapipe_solution = mediapipe_solution
        self.initialize_mediapipe()
        
    def initialize_mediapipe(self):
        """Initialize the selected MediaPipe solution"""
        if self.mediapipe_solution == "hands":
            self.mp_hands = mp.solutions.hands
            self.hands = self.mp_hands.Hands(
                static_image_mode=False,
                max_num_hands=2,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5
            )
            self.mp_drawing = mp.solutions.drawing_utils
            
        elif self.mediapipe_solution == "face":
            self.mp_face_mesh = mp.solutions.face_mesh
            self.face_mesh = self.mp_face_mesh.FaceMesh(
                static_image_mode=False,
                max_num_faces=1,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5
            )
            self.mp_drawing = mp.solutions.drawing_utils
            
        elif self.mediapipe_solution == "pose":
            self.mp_pose = mp.solutions.pose
            self.pose = self.mp_pose.Pose(
                static_image_mode=False,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5
            )
            self.mp_drawing = mp.solutions.drawing_utils
            
        elif self.mediapipe_solution == "holistic":
            self.mp_holistic = mp.solutions.holistic
            self.holistic = self.mp_holistic.Holistic(
                static_image_mode=False,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5
            )
            self.mp_drawing = mp.solutions.drawing_utils
            
        else:
            raise ValueError(f"Unsupported MediaPipe solution: {self.mediapipe_solution}")
    
    def get_frame(self):
        """Get a single frame from the ESP32 camera"""
        try:
            # For MJPEG streaming
            if self.esp32_url.endswith('.mjpg') or self.esp32_url.endswith('/stream'):
                resp = urllib.request.urlopen(self.esp32_url)
                bytes_data = bytes()
                while True:
                    bytes_data += resp.read(1024)
                    a = bytes_data.find(b'\xff\xd8')  # JPEG start
                    b = bytes_data.find(b'\xff\xd9')  # JPEG end
                    if a != -1 and b != -1:
                        jpg = bytes_data[a:b+2]
                        bytes_data = bytes_data[b+2:]
                        return cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
            
            # For single image endpoint
            else:
                resp = requests.get(self.esp32_url, stream=True).raw
                image = np.asarray(bytearray(resp.read()), dtype=np.uint8)
                return cv2.imdecode(image, cv2.IMREAD_COLOR)
                
        except URLError as e:
            print(f"Error accessing ESP32 camera: {e}")
            return None
        except Exception as e:
            print(f"Error getting frame: {e}")
            return None
    
    def process_frame(self, frame):
        """Process a frame with MediaPipe"""
        if frame is None:
            return None
        
        # Convert BGR to RGB for MediaPipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process with appropriate MediaPipe solution
        if self.mediapipe_solution == "hands":
            results = self.hands.process(rgb_frame)
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    self.mp_drawing.draw_landmarks(
                        frame, 
                        hand_landmarks, 
                        self.mp_hands.HAND_CONNECTIONS
                    )
                    
        elif self.mediapipe_solution == "face":
            results = self.face_mesh.process(rgb_frame)
            if results.multi_face_landmarks:
                for face_landmarks in results.multi_face_landmarks:
                    self.mp_drawing.draw_landmarks(
                        frame,
                        face_landmarks,
                        self.mp_face_mesh.FACEMESH_CONTOURS,
                        landmark_drawing_spec=self.mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=1, circle_radius=1),
                        connection_drawing_spec=self.mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=1)
                    )
                    
        elif self.mediapipe_solution == "pose":
            results = self.pose.process(rgb_frame)
            if results.pose_landmarks:
                self.mp_drawing.draw_landmarks(
                    frame,
                    results.pose_landmarks,
                    self.mp_pose.POSE_CONNECTIONS
                )
                
        elif self.mediapipe_solution == "holistic":
            results = self.holistic.process(rgb_frame)
            # Draw face landmarks
            if results.face_landmarks:
                self.mp_drawing.draw_landmarks(
                    frame,
                    results.face_landmarks,
                    self.mp_holistic.FACEMESH_CONTOURS,
                    landmark_drawing_spec=self.mp_drawing.DrawingSpec(color=(80, 110, 10), thickness=1, circle_radius=1),
                    connection_drawing_spec=self.mp_drawing.DrawingSpec(color=(80, 256, 121), thickness=1)
                )
            # Draw pose landmarks
            if results.pose_landmarks:
                self.mp_drawing.draw_landmarks(
                    frame,
                    results.pose_landmarks,
                    self.mp_holistic.POSE_CONNECTIONS
                )
            # Draw hand landmarks
            for hand_landmarks in [results.left_hand_landmarks, results.right_hand_landmarks]:
                if hand_landmarks:
                    self.mp_drawing.draw_landmarks(
                        frame,
                        hand_landmarks,
                        self.mp_holistic.HAND_CONNECTIONS
                    )
        
        return frame
    
    def run(self):
        """Main processing loop"""
        print(f"Connecting to ESP32 camera at {self.esp32_url}")
        print(f"Processing with MediaPipe {self.mediapipe_solution}")
        
        while True:
            start_time = time.time()
            
            # Get frame from ESP32
            frame = self.get_frame()
            if frame is None:
                print("Failed to get frame, retrying in 1 second...")
                time.sleep(1)
                continue
            
            # Process frame with MediaPipe
            processed_frame = self.process_frame(frame)
            
            # Calculate FPS
            fps = 1.0 / (time.time() - start_time)
            cv2.putText(processed_frame, f"FPS: {fps:.2f}", (10, 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            # Display the frame
            cv2.imshow('ESP32 Camera with MediaPipe', processed_frame)
            
            # Press 'q' to exit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        cv2.destroyAllWindows()

# Example usage
if __name__ == "__main__":
    # Replace with your ESP32 camera URL
    # Examples:
    # - For ESP32-CAM running the default CameraWebServer example: "http://esp32-ip-address/stream"
    # - For a single JPEG image: "http://esp32-ip-address/capture"
    # - For MJPEG stream: "http://esp32-ip-address:81/stream"
    
    ESP32_URL = "http://192.168.1.7:81/stream"  # Replace with your ESP32 camera URL
    
    # Choose MediaPipe solution: "hands", "face", "pose", or "holistic"
    SOLUTION = "hands"
    
    processor = ESP32CameraProcessor(ESP32_URL, SOLUTION)
    processor.run()