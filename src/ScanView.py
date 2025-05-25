from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFileDialog,
    QProgressBar, QListWidget, QMessageBox, QSizePolicy
)
from PyQt5.QtGui import QPixmap, QPainter, QPen, QImage, QColor
from PyQt5.QtCore import Qt, pyqtSignal
from utils import resource_path # Added import
import os
import shutil
from datetime import datetime
from InferenceWorker import InferenceWorker
import json


from PyQt5.QtWidgets import QLabel, QSizePolicy
from PyQt5.QtGui import QPixmap, QPainter, QPen
from PyQt5.QtCore import Qt, pyqtSignal

# Drop your BODY_REGIONS here (from your previous message)
BODY_REGIONS = [
    {'name': 'Head (Front)', 'rect': (235, 84, 370, 220)},
    {'name': 'Neck (Front)', 'rect': (263, 216, 345, 244)},
    {'name': 'Chest', 'rect': (220, 244, 391, 390)},
    {'name': 'Abdomen', 'rect': (232, 390, 391, 500)},
    {'name': 'Pelvis', 'rect': (222, 500, 395, 575)},
    {'name': 'Left Upper Arm (Front)',  'rect': (165, 244, 221, 407)},
    {'name': 'Left Lower Arm (Front)',  'rect': (110, 407, 211, 527)},
    {'name': 'Left Hand (Front)',       'rect': (104, 527, 197, 625)},
    {'name': 'Right Upper Arm (Front)', 'rect': (387, 244, 450, 407)},
    {'name': 'Right Lower Arm (Front)', 'rect': (388, 407, 470, 527)},
    {'name': 'Right Hand (Front)',      'rect': (412, 527, 504, 625)},
    {'name': 'Left Upper Leg (Front)',  'rect': (209, 575, 301, 726)},
    {'name': 'Left Lower Leg (Front)',  'rect': (217, 726, 297, 886)},
    {'name': 'Left Foot (Front)',       'rect': (231, 886, 299, 944)},
    {'name': 'Right Upper Leg (Front)', 'rect': (305, 575, 394, 726)},
    {'name': 'Right Lower Leg (Front)', 'rect': (311, 726, 381, 886)},
    {'name': 'Right Foot (Front)',      'rect': (310, 886, 386, 944)},
    {'name': 'Head (Back)', 'rect': (650, 84, 780, 220)},
    {'name': 'Neck (Back)', 'rect': (678, 216, 760, 244)},
    {'name': 'Upper Back', 'rect': (635, 244, 808, 390)},
    {'name': 'Lower Back', 'rect': (647, 390, 810, 500)},
    {'name': 'Buttox', 'rect': (637, 500, 810, 585)},
    {'name': 'Left Upper Arm (Back)', 'rect': (580, 244, 639, 407)},
    {'name': 'Left Lower Arm (Back)', 'rect': (525, 407, 629, 527)},
    {'name': 'Left Hand (Back)', 'rect': (519, 527, 615, 625)},
    {'name': 'Right Upper Arm (Back)', 'rect': (802, 244, 868, 407)},
    {'name': 'Right Lower Arm (Back)', 'rect': (803, 407, 888, 527)},
    {'name': 'Right Hand (Back)', 'rect': (827, 527, 922, 625)},
    {'name': 'Left Upper Leg (Back)', 'rect': (624, 585, 719, 726)},
    {'name': 'Left Lower Leg (Back)', 'rect': (632, 726, 715, 886)},
    {'name': 'Left Foot (Back)', 'rect': (646, 886, 717, 944)},
    {'name': 'Right Upper Leg (Back)', 'rect': (720, 585, 812, 726)},
    {'name': 'Right Lower Leg (Back)', 'rect': (726, 726, 799, 886)},
    {'name': 'Right Foot (Back)', 'rect': (725, 886, 804, 944)}
]

def get_body_region(x_img, y_img):
    for region in BODY_REGIONS:
        x0, y0, x1, y1 = region['rect']
        if x0 <= x_img < x1 and y0 <= y_img < y1:
            return region['name']
    return "Unknown area"

class BodyMap(QLabel):
    clicked = pyqtSignal(int, int)  # x_img, y_img (original image space)

    def __init__(self, img_path, parent=None):
        super().__init__(parent)
        self.img_path = img_path
        self.setAlignment(Qt.AlignCenter)
        self.setCursor(Qt.PointingHandCursor)
        self.selected_point = None  # display coordinates
        self.original_pixmap = QPixmap(self.img_path)
        self.setPixmap(self.scaled_pixmap())
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setPixmap(self.scaled_pixmap())
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def resizeEvent(self, event):
        self.setPixmap(self.scaled_pixmap())
        self.update()
        super().resizeEvent(event)

    def scaled_pixmap(self):
        return self.original_pixmap.scaled(
            self.width(), self.height(), Qt.KeepAspectRatio, Qt.SmoothTransformation
        )

    def mousePressEvent(self, event):
        pixmap = self.pixmap()
        if pixmap is None:
            return
        pixmap_width, pixmap_height = pixmap.width(), pixmap.height()
        label_width, label_height = self.width(), self.height()
        offset_x = (label_width - pixmap_width) // 2
        offset_y = (label_height - pixmap_height) // 2
        x_disp, y_disp = event.x(), event.y()
        if (offset_x <= x_disp < offset_x + pixmap_width) and (offset_y <= y_disp < offset_y + pixmap_height):
            x_in_pixmap = x_disp - offset_x
            y_in_pixmap = y_disp - offset_y
            orig_width = self.original_pixmap.width()
            orig_height = self.original_pixmap.height()
            x_img = int(x_in_pixmap * orig_width / pixmap_width)
            y_img = int(y_in_pixmap * orig_height / pixmap_height)
            self.selected_point = (x_disp, y_disp)
            self.clicked.emit(x_img, y_img)
            self.update()

    def paintEvent(self, event):
        # Draw the pixmap
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        pixmap = self.scaled_pixmap()
        x = (self.width() - pixmap.width()) // 2
        y = (self.height() - pixmap.height()) // 2
        painter.drawPixmap(x, y, pixmap)

        # Draw blue dot if selected
        if self.selected_point:
            x_disp, y_disp = self.selected_point
            painter.setPen(QPen(QColor(30, 144, 255), 3))
            painter.setBrush(QColor(30, 144, 255))
            painter.drawEllipse(x_disp - 7, y_disp - 7, 7, 7)
        painter.end()


class ScanView(QWidget):
    def __init__(self, get_current_profile_func):
        super().__init__()
        self.selected_location = None
        self.selected_body_part = None
        self.selected_file_path = None
        self.result_image_path = None
        self.selected_side = None
        self.inference_worker = None
        self.get_current_profile_func = get_current_profile_func

        self.setStyleSheet("""
            QLabel#ProfileLabel { font-size: 15px; color: #eee; }
            QLabel#Instructions { font-size: 22px; font-weight: bold; margin-bottom: 16px; color: #fff; }
            QLabel#FileLabel { font-size: 15px; color: #ccc; }
            QLabel#ResultLabel { font-size: 16px; margin: 5px 0; }
            QPushButton { font-size: 15px; }
            QListWidget, QProgressBar { font-size: 15px; }
            QListWidget { background: #232323; color: #fff; border-radius: 7px; }
        """)
        self.button_style = """
            QPushButton#MainAction {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #22b6b2, stop:1 #1f78be
                );
                color: #fff;
                border: none;
                border-radius: 16px;
                font-size: 17px;
                font-weight: bold;
                padding: 11px 10px;
                margin-top: 4px;
                margin-bottom: 4px;
            }
            QPushButton#MainAction:hover {
                background: qlineargradient(
                    x1:0, y1:1, x2:1, y2:0,
                    stop:0 #29cccc, stop:1 #2b93c0
                );
                color: #fff;
            }
            QPushButton#SaveAction {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #ff726f, stop:1 #fa377d
                );
                color: #fff;
                border: none;
                border-radius: 16px;
                font-size: 17px;
                font-weight: bold;
                padding: 11px 34px;
                margin-top: 7px;
                margin-bottom: 7px;
            }
            QPushButton#SaveAction:hover {
                background: qlineargradient(
                    x1:0, y1:1, x2:1, y2:0,
                    stop:0 #e53e3e, stop:1 #fa377d
                );
                color: #fff;
            }
            QLabel#ResultCard {
                font-size:15px;
                color:#fff;
                background:rgba(30,30,30,0.93);
                border-radius:16px;
                padding: 15px 15px 15px 15px;
                margin-top:12px;
                margin-bottom:8px;
                min-width: 310px;
                max-width: 400px;
                min-height: 100px;
                max-height: 300px;
            }
        """
        self.setStyleSheet(self.styleSheet() + self.button_style)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(38, 25, 38, 20)
        main_layout.setSpacing(0)
        self.setLayout(main_layout)

        # Header: Instructions and Profile
        self.profile_label = QLabel()
        self.profile_label.setStyleSheet("font-size:17px;color:#fff;")
        self.profile_label.setAlignment(Qt.AlignCenter)
        self.profile_label.setObjectName("ProfileLabel")
        main_layout.addWidget(self.profile_label)

        self.instructions = QLabel(
            "<b>Step 1:</b> Click the body map to select a body part.<br>"
            "<b>Step 2:</b> Upload a lesion photo for analysis."
        )
        self.instructions.setObjectName("Instructions")
        self.instructions.setAlignment(Qt.AlignCenter)
        self.instructions.setWordWrap(True)
        main_layout.addWidget(self.instructions)
        main_layout.addSpacing(18)

        # --- Central Row Layout (Body map | Results) ---
        central_row = QHBoxLayout()
        central_row.setSpacing(44)
        main_layout.addLayout(central_row, stretch=1)

        # ---- LEFT COLUMN: Body Map + Controls ----
        left_col = QVBoxLayout()
        left_col.setAlignment(Qt.AlignTop)
        left_col.setSpacing(10)
        central_row.addLayout(left_col, stretch=1)

        # Body map
        self.body_map = BodyMap(resource_path("Resources/icon_body.png")) # Modified line
        self.body_map.setMinimumHeight(340)
        self.body_map.setMaximumWidth(360)
        self.body_map.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        left_col.addWidget(self.body_map, alignment=Qt.AlignHCenter)
        left_col.addSpacing(10)

        # Upload controls row
        upload_row = QHBoxLayout()
        left_col.addLayout(upload_row)
        left_col.addSpacing(4)

        # Progress bar
        self.progress = QProgressBar()
        self.progress.setFixedHeight(20)
        self.progress.setValue(0)
        left_col.addWidget(self.progress)
        left_col.addStretch(1)

        # ---- RIGHT COLUMN: Results ----
        right_col = QVBoxLayout()
        right_col.setAlignment(Qt.AlignTop)
        right_col.setSpacing(14)
        central_row.addLayout(right_col, stretch=2)

        # Result image
        self.result_image_label = QLabel()
        self.result_image_label.setAlignment(Qt.AlignCenter)
        self.result_image_label.setScaledContents(True)
        self.result_image_label.setMaximumWidth(430)
        self.result_image_label.setMinimumHeight(210)
        self.result_image_label.setVisible(False)
        right_col.addWidget(self.result_image_label, alignment=Qt.AlignHCenter)
        right_col.addSpacing(6)

        # Upload Button
        self.upload_btn = QPushButton("Upload Lesion Photo")
        self.upload_btn.setObjectName("MainAction")
        self.upload_btn.setMinimumWidth(200)
        upload_row.addWidget(self.upload_btn, alignment=Qt.AlignLeft)
        self.selected_file_label = QLabel("Selected file: None")
        self.selected_file_label.setObjectName("FileLabel")
        upload_row.addWidget(self.selected_file_label, alignment=Qt.AlignLeft)

        # Save Button (in right_col)
        self.save_btn = QPushButton("Save Scan to Profile")
        self.save_btn.setObjectName("SaveAction")
        self.save_btn.setVisible(False)
        right_col.addWidget(self.save_btn, alignment=Qt.AlignHCenter)

        # Result Label (card-like box)
        self.result_label = QLabel("Your results will appear here.")
        self.result_label.setObjectName("ResultCard")
        self.result_label.setAlignment(Qt.AlignCenter)
        self.result_label.setWordWrap(True)
        right_col.addWidget(self.result_label, alignment=Qt.AlignHCenter)

        main_layout.addSpacing(18)
        main_layout.addWidget(QLabel("<b>Previous Scans:</b>"))
        self.history_list = QListWidget()
        self.history_list.setMaximumHeight(80)
        main_layout.addWidget(self.history_list)

        self.history_disclaimer = QLabel("No scans saved in Guest mode.")
        self.history_disclaimer.setStyleSheet("""
            color: #bbb;
            font-size: 15px;
            font-style: italic;
            margin-top: 10px;
        """)
        self.history_disclaimer.setAlignment(Qt.AlignCenter)
        self.history_disclaimer.setVisible(False)
        main_layout.addWidget(self.history_disclaimer)

        # Signals
        self.body_map.clicked.connect(self.handle_body_click)
        self.upload_btn.clicked.connect(self.open_file_dialog)
        self.save_btn.clicked.connect(self.save_result_to_profile)

    # --- Profile Switching Handler ---
    def on_profile_switched(self):
        self.selected_location = None
        self.selected_body_part = None
        self.selected_file_path = None
        self.result_image_path = None
        self.selected_side = None
        self.body_map.selected_point = None
        self.body_map.update()
        self.instructions.setText(
            "<b>Step 1:</b> Click the body map to select a body part.<br>"
            "<b>Step 2:</b> Upload a lesion photo for analysis."
        )
        self.result_label.setText("Your results will appear here.")
        self.history_list.clear()
        self.update_profile_display(self.get_current_profile_func().get("name", "None"))
        self.update_save_button_visibility()
        self.update_history_disclaimer()

    def update_profile_display(self, profile_name):
        if profile_name:
            self.profile_label.setText(f"<b>Current Profile:</b> {profile_name}")
        else:
            self.profile_label.setText("<b>Current Profile:</b> None")

    def update_save_button_visibility(self):
        profile = self.get_current_profile_func()
        if profile and profile.get("id") == "guest":
            self.save_btn.setVisible(False)
        else:
            self.save_btn.setVisible(True)

    def update_history_disclaimer(self):
        profile = self.get_current_profile_func()
        if profile and profile.get("id") == "guest":
            self.history_list.setVisible(False)
            self.history_disclaimer.setText("No scans saved in Guest mode.")
            self.history_disclaimer.setVisible(True)
        elif self.history_list.count() == 0:
            self.history_list.setVisible(False)
            self.history_disclaimer.setText("No scans saved yet for this profile.")
            self.history_disclaimer.setVisible(True)
        else:
            self.history_list.setVisible(True)
            self.history_disclaimer.setVisible(False)

    def handle_body_click(self, x, y):
        self.selected_location = (x, y)
        self.selected_body_part = get_body_region(x, y)
        self.instructions.setText(
            f"<b>Body part selected:</b> {self.selected_body_part}<br>Now upload a lesion photo for analysis."
        )
        self.body_map.update()

    def open_file_dialog(self):
        if not self.selected_body_part:
            QMessageBox.warning(self, "Location Required", "Please select a body part on the map first.")
            return
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Select Lesion Photo", "", "Images (*.png *.jpg *.jpeg *.bmp)"
        )
        if file_name:
            self.selected_file_path = file_name
            self.selected_file_label.setText(f"Selected file: {os.path.basename(file_name)}")
            self.run_inference(file_name)

    def run_inference(self, file_path):
        self.result_label.setText("Processing image, please wait...")
        self.progress.setValue(10)
        self.result_image_label.setVisible(False)
        self.save_btn.setVisible(False)
        self.inference_worker = InferenceWorker(file_path)
        self.inference_worker.progress.connect(self.progress.setValue)
        self.inference_worker.finished.connect(self.display_result)
        self.inference_worker.error.connect(self.handle_inference_error)
        self.inference_worker.start()

    def display_result(self, result):
        self.progress.setValue(100)
        m, n, img_path = result if len(result) == 3 else (*result, None)

        # Store for saving
        self.last_m = m
        self.last_n = n
        self.last_img_path = img_path

        risk_text = (
            f"<span style='font-size:18px;'><b>Melanoma likelihood:</b> "
            f"<span style='color:#e34a6f'>{m:.1f}%</span><br>"
            f"<b>Non-melanoma likelihood:</b> <span style='color:#22b6b2'>{n:.1f}%</span></span><br>"
        )
        if m > 50:
            risk_text += '<div style="color:#e34a6f;font-weight:bold;font-size:17px;">High risk! Please consult a doctor.</div>'
        elif m > 30:
            risk_text += '<div style="color:#f08a24;font-weight:bold;font-size:17px;">Moderate risk. Monitor closely and consult as needed.</div>'
        else:
            risk_text += '<div style="color:#22b6b2;font-weight:bold;font-size:17px;">Low risk. Continue to observe and protect your skin.</div>'
        self.result_label.setText(risk_text)
        self.update_save_button_visibility()

        if img_path and os.path.exists(img_path):
            pix = QPixmap(img_path).scaled(400, 400, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.result_image_label.setPixmap(pix)
            self.result_image_label.setVisible(True)
            self.result_image_path = img_path
        else:
            self.result_image_label.setVisible(False)
            self.result_image_path = None

        profile = self.get_current_profile_func()
        if not (profile and profile.get("id") == "guest"):
            self.history_list.addItem(
                f"{datetime.now():%Y-%m-%d %H:%M} — Melanoma: {m:.1f}% | Non-melanoma: {n:.1f}%"
            )
        else:
            self.history_list.clear()

        self.save_btn.setText("Save Scan to Profile")
        self.save_btn.setEnabled(True)
        self.save_btn.setStyleSheet("")
        self.update_history_disclaimer()


    def save_result_to_profile(self):
        current_profile = self.get_current_profile_func()
        if not current_profile or current_profile.get("id") == "guest":
            QMessageBox.warning(self, "Guest Mode", "Guests cannot save scans. Please select a user profile.")
            return
        profile_id = current_profile.get('id', current_profile.get('name', 'default'))
        scan_dir = os.path.join("profile_scans", str(profile_id))
        os.makedirs(scan_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        dest_img = None
        if self.result_image_path and os.path.exists(self.result_image_path):
            dest_img = os.path.join(scan_dir, f"scan_{timestamp}.jpg")
            shutil.copyfile(self.result_image_path, dest_img)
        scan_meta = {
            "timestamp": timestamp,
            "body_part": f"{self.selected_body_part}",
            "melanoma_likelihood": float(getattr(self, "last_m", 0.0)),
            "non_melanoma_likelihood": float(getattr(self, "last_n", 0.0)),
            "image_path": dest_img
        }

        scans_json = os.path.join(scan_dir, "scans.json")
        scans = []
        if os.path.exists(scans_json):
            with open(scans_json, "r") as f:
                scans = json.load(f)
        scans.append(scan_meta)
        with open(scans_json, "w") as f:
            json.dump(scans, f, indent=2)
        QMessageBox.information(self, "Saved", "Scan result saved to profile!")
        self.save_btn.setText("Scan saved to profile")
        self.save_btn.setEnabled(False)
        self.save_btn.setStyleSheet("""
            background: #5ec77e;
            color: #fff;
            border: none;
            border-radius: 16px;
            font-size: 17px;
            font-weight: bold;
            padding: 11px 34px;
            margin-top: 7px;
            margin-bottom: 7px;
        """)
        # Refresh scan history
        parent = self.parent()
        while parent is not None:
            if hasattr(parent, 'monitor_tab'):
                parent.monitor_tab.load_scans()
                break
            parent = parent.parent()
        self.history_list.addItem(
            f"{datetime.now():%Y-%m-%d %H:%M} — Melanoma: {scan_meta['melanoma_likelihood']:.1f}% | Non-melanoma: {scan_meta['non_melanoma_likelihood']:.1f}%"
        )

        self.update_history_disclaimer()

    def handle_inference_error(self, msg):
        QMessageBox.critical(self, "Inference Error", msg)
        self.progress.setValue(0)
        self.result_label.setText("Error processing image. Please try again.")
        self.result_image_label.setVisible(False)
        self.save_btn.setVisible(False)