from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QListWidget, QLineEdit, QHBoxLayout,
    QMessageBox, QFormLayout, QDialog, QDialogButtonBox
)
import json
import os
import uuid

PROFILE_FILE = "profiles.json"

class ProfileEditDialog(QDialog):
    def __init__(self, profile=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Profile" if profile else "New Profile")
        self.setModal(True)
        layout = QFormLayout(self)

        self.name_input = QLineEdit(profile["name"] if profile else "")
        self.name_input.setPlaceholderText("Name")
        layout.addRow("Name*", self.name_input)

        self.age_input = QLineEdit(str(profile["age"]) if profile and "age" in profile else "")
        self.age_input.setPlaceholderText("Optional")
        layout.addRow("Age", self.age_input)

        self.gender_input = QLineEdit(profile["gender"] if profile and "gender" in profile else "")
        self.gender_input.setPlaceholderText("Optional (e.g. Female, Male, Non-binary, etc.)")
        layout.addRow("Gender", self.gender_input)

        self.ethnicity_input = QLineEdit(profile["ethnicity"] if profile and "ethnicity" in profile else "")
        self.ethnicity_input.setPlaceholderText("Optional")
        layout.addRow("Ethnicity", self.ethnicity_input)

        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)

    def get_profile(self):
        return {
            "name": self.name_input.text().strip(),
            "age": self.age_input.text().strip(),
            "gender": self.gender_input.text().strip(),
            "ethnicity": self.ethnicity_input.text().strip()
        }

class ProfileManager(QWidget):
    def __init__(self, on_profile_changed=None):
        super().__init__()
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(28, 18, 28, 18)
        main_layout.setSpacing(14)

        # Heading and privacy info
        title = QLabel("<h2 style='color:#22b6b2;'>User Profiles</h2>")
        main_layout.addWidget(title)
        desc = QLabel(
            "Manage user or patient profiles below. "
            "Profile details help track scan history separately and personalise your experience.<br>"
            "<span style='color:#666; font-size:14px;'>All stored information is optional and private as it is only stored on this device.</span>"
        )
        desc.setWordWrap(True)
        main_layout.addWidget(desc)

        # Profile list and buttons
        list_row = QHBoxLayout()
        self.profile_list = QListWidget()
        self.profile_list.setToolTip("Select a profile to view, edit, or delete")
        self.profile_list.setMinimumWidth(200)
        self.profile_list.setStyleSheet("""
            QListWidget::item:selected { background: #22b6b2; color: #fff; }
            QListWidget::item { padding: 10px; font-size: 16px; }
        """)
        list_row.addWidget(self.profile_list)

        # Profile action buttons
        btn_col = QVBoxLayout()
        self.add_btn = QPushButton("Add Profile")
        self.add_btn.setToolTip("Create a new user or patient profile")
        btn_col.addWidget(self.add_btn)
        self.edit_btn = QPushButton("Edit Profile")
        self.edit_btn.setToolTip("Edit the selected profile")
        btn_col.addWidget(self.edit_btn)
        self.delete_btn = QPushButton("Delete Profile")
        self.delete_btn.setToolTip("Delete the selected profile (irreversible)")
        btn_col.addWidget(self.delete_btn)
        btn_col.addStretch(1)
        list_row.addLayout(btn_col)
        main_layout.addLayout(list_row)

        # Selected profile details
        self.profile_detail = QLabel("No profile selected.")
        self.profile_detail.setStyleSheet("background: #22b6b2; border-radius: 14px; padding: 10px 16px; margin: 8px 0;")
        main_layout.addWidget(self.profile_detail)

        # Signal connections
        self.add_btn.clicked.connect(self.add_profile)
        self.edit_btn.clicked.connect(self.edit_profile)
        self.delete_btn.clicked.connect(self.delete_profile)
        self.profile_list.currentRowChanged.connect(self.display_profile_details)
        self.on_profile_changed = on_profile_changed
        self.profile_list.currentRowChanged.connect(self.profile_selected)

    def load_profiles(self, select_idx=None):
        self.profile_list.clear()
        self.profiles = [{"name": "Guest", "id": "guest"}]  # Add Guest as first option
        if os.path.isfile(PROFILE_FILE):
            with open(PROFILE_FILE, "r") as f:
                self.profiles += json.load(f)
        for profile in self.profiles:
            label = profile.get("name", "(unnamed)")
            self.profile_list.addItem(label)
        # Reselect previous/newly created/edited profile if any
        if select_idx is not None and 0 <= select_idx < len(self.profiles):
            self.profile_list.setCurrentRow(select_idx)
        elif self.profiles:
            self.profile_list.setCurrentRow(0)
        else:
            self.profile_detail.setText("No profile selected.")
        if self.on_profile_changed:
            self.on_profile_changed(self.get_current_profile())        

    def save_profiles(self):
        # Only save non-Guest profiles
        profiles_to_save = [p for p in self.profiles if p.get("id") != "guest"]
        with open(PROFILE_FILE, "w") as f:
            json.dump(profiles_to_save, f, indent=2)


    def add_profile(self):
        dlg = ProfileEditDialog(parent=self)
        if dlg.exec_() == QDialog.Accepted:
            new_profile = dlg.get_profile()
            if not new_profile["name"]:
                QMessageBox.warning(self, "Input Required", "Please enter at least a name for the profile.")
                return
            if "id" not in new_profile:
                new_profile["id"] = uuid.uuid4().hex
            self.profiles.append(new_profile)
            self.save_profiles()
            self.load_profiles(select_idx=len(self.profiles)-1)

    def edit_profile(self):
        idx = self.profile_list.currentRow()
        if idx < 0 or idx >= len(self.profiles):
            QMessageBox.warning(self, "Select Profile", "Please select a profile to edit.")
            return
        profile = self.profiles[idx]
        if profile.get("id") == "guest":
            QMessageBox.information(self, "Not allowed", "The Guest profile cannot be edited.")
            return
        dlg = ProfileEditDialog(profile, parent=self)
        if dlg.exec_() == QDialog.Accepted:
            updated_profile = dlg.get_profile()
            updated_profile["id"] = profile.get("id", uuid.uuid4().hex)
            self.profiles[idx] = updated_profile
            self.save_profiles()
            self.load_profiles(select_idx=idx)

    def delete_profile(self):
        idx = self.profile_list.currentRow()
        if idx < 0 or idx >= len(self.profiles):
            QMessageBox.warning(self, "Select Profile", "Please select a profile to delete.")
            return
        profile = self.profiles[idx]
        if profile.get("id") == "guest":
            QMessageBox.information(self, "Not allowed", "The Guest profile cannot be deleted.")
            return
        reply = QMessageBox.question(
            self, "Confirm Deletion",
            f"Are you sure you want to delete the profile '{self.profiles[idx]['name']}'? This cannot be undone.",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            del self.profiles[idx]
            self.save_profiles()
            self.load_profiles(select_idx=0 if self.profiles else None)

    def display_profile_details(self, idx):
        if idx < 0 or idx >= len(self.profiles):
            self.profile_detail.setText("No profile selected.")
            self.edit_btn.setEnabled(False)
            self.delete_btn.setEnabled(False)
            return
        p = self.profiles[idx]
        detail = (
            f"<b>Name:</b> {p.get('name','')}<br>"
            f"<b>Age:</b> {p.get('age','')}<br>"
            f"<b>Gender:</b> {p.get('gender','')}<br>"
            f"<b>Ethnicity:</b> {p.get('ethnicity','')}"
        )
        self.profile_detail.setText(detail)
        is_guest = p.get("id") == "guest"
        self.edit_btn.setEnabled(not is_guest)
        self.delete_btn.setEnabled(not is_guest)


    def get_current_profile(self):
        idx = self.profile_list.currentRow()
        if idx < 0 or not hasattr(self, 'profiles') or idx >= len(self.profiles):
            return None
        return self.profiles[idx]
    
    def profile_selected(self, idx):
        if self.on_profile_changed:
            self.on_profile_changed(self.get_current_profile())
