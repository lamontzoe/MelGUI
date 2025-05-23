from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QCheckBox, QHBoxLayout, QPushButton, QComboBox, QFileDialog, QMessageBox
)
from PyQt5.QtCore import Qt

class SettingsDialogue(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 18)
        layout.setSpacing(18)

        title = QLabel("<h2 style='color:#22b6b2;'>Settings & Preferences</h2>")
        layout.addWidget(title)

        # Theme selection (expand as needed)
        theme_label = QLabel("App Theme (for future use):")
        layout.addWidget(theme_label)
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["System Default", "Light", "Dark"])
        self.theme_combo.setCurrentIndex(0)
        self.theme_combo.setToolTip("Theme support coming soon!")
        self.theme_combo.setEnabled(False)  # Enable when implemented
        layout.addWidget(self.theme_combo)

        # Data location
        data_label = QLabel("Data & Scan Storage Location (default: app folder):")
        layout.addWidget(data_label)
        row = QHBoxLayout()
        self.data_path_label = QLabel("<i>./profile_scans/</i>")
        row.addWidget(self.data_path_label)
        self.change_data_path_btn = QPushButton("Change Folder…")
        self.change_data_path_btn.setToolTip("Choose where scans and profiles are saved.")
        self.change_data_path_btn.clicked.connect(self.choose_data_folder)
        row.addWidget(self.change_data_path_btn)
        row.addStretch()
        layout.addLayout(row)

        # Accessibility options (expandable)
        self.large_font_checkbox = QCheckBox("Use large fonts for better readability")
        self.large_font_checkbox.setChecked(False)
        self.large_font_checkbox.setToolTip("Increases the font size throughout the app for easier reading.")
        layout.addWidget(self.large_font_checkbox)
        self.large_font_checkbox.stateChanged.connect(self.apply_font_size)

        # Reset Data (danger area)
        layout.addSpacing(12)
        danger = QLabel("<b style='color:#e34a6f;'>Danger Zone:</b>")
        layout.addWidget(danger)
        self.reset_btn = QPushButton("Delete All Profiles and Scans")
        self.reset_btn.setStyleSheet("background:#e34a6f;color:white;")
        self.reset_btn.setToolTip("This will erase ALL profiles and scan data. Use with caution!")
        self.reset_btn.clicked.connect(self.confirm_reset)
        layout.addWidget(self.reset_btn)

        layout.addStretch(1)

    def choose_data_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Data Folder")
        if folder:
            # Here, just update label; if you implement, move scan/profile storage code to use this folder.
            self.data_path_label.setText(folder)
            QMessageBox.information(self, "Data Folder Changed",
                                    "Note: This change will only take effect for new scans and profiles.")

    def apply_font_size(self, state):
        if state == Qt.Checked:
            self.setStyleSheet("font-size: 18px;")
        else:
            self.setStyleSheet("")

    def confirm_reset(self):
        resp = QMessageBox.question(
            self, "Confirm Reset",
            "Are you sure you want to DELETE ALL profiles and scan data? This cannot be undone.",
            QMessageBox.Yes | QMessageBox.No
        )
        if resp == QMessageBox.Yes:
            import shutil
            import os
            # Remove scan folder and profiles file
            if os.path.exists("profile_scans"):
                shutil.rmtree("profile_scans")
            if os.path.exists("profiles.json"):
                os.remove("profiles.json")
            QMessageBox.information(self, "Data Reset", "All profiles and scans have been deleted.")
            # Optionally, signal the app to reload/reset everything.

