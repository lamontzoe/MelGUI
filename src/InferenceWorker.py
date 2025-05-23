from PyQt5.QtCore import QThread, pyqtSignal
from ultralytics import YOLO
import os
import traceback
import cv2

class InferenceWorker(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(tuple)  # (melanoma %, non-melanoma %, saved_image_path)
    error = pyqtSignal(str)

    def __init__(self, file_path, model_path='models/best.pt'):
        super().__init__()
        self.file_path = file_path
        self.model_path = model_path

    def run(self):
        try:
            self.progress.emit(10)
            if not os.path.exists(self.file_path):
                self.error.emit("Selected image not found.")
                return
            if not os.path.exists(self.model_path):
                self.error.emit("YOLO model file not found.")
                return

            self.progress.emit(30)
            model = YOLO(self.model_path)
            self.progress.emit(50)
            results = model(self.file_path, save=False)
            self.progress.emit(70)

            detections = []
            if hasattr(results[0], "boxes") and results[0].boxes is not None:
                for box in results[0].boxes:
                    cls = int(box.cls)
                    conf = float(box.conf)
                    xyxy = box.xyxy.cpu().numpy().astype(int)[0]
                    detections.append({"cls": cls, "conf": conf, "xyxy": xyxy})

            img = cv2.imread(self.file_path)
            mel = 0.0
            non_mel = 100.0
            box_color = (178, 182, 34)  # default teal for low risk

            if detections:
                top_det = max(detections, key=lambda d: d["conf"])
                x1, y1, x2, y2 = top_det["xyxy"]
                if top_det["cls"] == 1:
                    mel = top_det["conf"] * 100
                    non_mel = 100 - mel
                else:
                    non_mel = top_det["conf"] * 100
                    mel = 100 - non_mel

                # Choose color based on risk
                if mel > 50:
                    box_color = (111, 74, 227)    # red/pinkish
                elif mel > 30:
                    box_color = (36, 138, 240)    # orange
                else:
                    box_color = (178, 182, 34)    # teal

                cv2.rectangle(img, (x1, y1), (x2, y2), box_color, 3)
            else:
                # No detections, leave as teal (default)
                pass

            save_path = os.path.splitext(self.file_path)[0] + "_result.jpg"
            cv2.imwrite(save_path, img)

            self.progress.emit(100)
            self.finished.emit((mel, non_mel, save_path))
        except Exception as e:
            traceback.print_exc()
            self.error.emit("Model inference failed. Please try again.")
