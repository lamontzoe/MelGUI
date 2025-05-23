from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QPushButton, QMessageBox, QHeaderView, QAbstractItemView, QDialog
)
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt
import os
import json
import re
from datetime import datetime
from functools import partial

class MonitorTab(QWidget):
    def __init__(self, get_current_profile_func, on_profile_changed_signal=None):
        super().__init__()
        self.get_current_profile_func = get_current_profile_func
        self.current_profile = None
        self.scan_data = []

        # Layout setup
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(28, 18, 28, 18)
        main_layout.setSpacing(10)
        self.setLayout(main_layout)

        # Header label
        self.header_label = QLabel()
        self.header_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #fff; margin-bottom: 14px;")
        self.header_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.header_label)

        # Sorting controls row (add more controls here if needed)
        sort_row = QHBoxLayout()
        sort_row.addStretch()
        main_layout.addLayout(sort_row)

        # Scan history table
        self.scan_table = QTableWidget()
        self.scan_table.setColumnCount(6)
        self.scan_table.setHorizontalHeaderLabels([
            "Date/Time", "Body Part", "Melanoma %", "Risk Level", "Image", "Delete"
        ])
        self.scan_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.scan_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.scan_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.scan_table.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.scan_table.setDragDropOverwriteMode(False)
        self.scan_table.setDragDropMode(QAbstractItemView.InternalMove)
        self.scan_table.setDefaultDropAction(Qt.MoveAction)
        self.scan_table.setDropIndicatorShown(True)
        self.scan_table.setSortingEnabled(True)
        main_layout.addWidget(self.scan_table, stretch=1)

        # Delete Selected button
        self.delete_selected_btn = QPushButton("Delete Selected")
        self.delete_selected_btn.setStyleSheet(
            "background:#ff5a5a; color:#fff; border:none; border-radius:9px; font-weight:bold; margin-top:8px;")
        self.delete_selected_btn.clicked.connect(self.delete_selected_scans)
        self.delete_selected_btn.setVisible(False)
        main_layout.addWidget(self.delete_selected_btn)

        # Guest disclaimer
        self.guest_disclaimer = QLabel("No history can be saved using Guest profile.")
        self.guest_disclaimer.setStyleSheet("""
            color: #bbb;
            font-size: 16px;
            font-style: italic;
            margin: 20px;
        """)
        self.guest_disclaimer.setAlignment(Qt.AlignCenter)
        self.guest_disclaimer.setVisible(False)
        main_layout.addWidget(self.guest_disclaimer)

        # Connect signals
        self.scan_table.cellClicked.connect(self.handle_table_click)
        self.scan_table.model().rowsMoved.connect(self.on_rows_moved)
        self.scan_table.selectionModel().selectionChanged.connect(self.on_selection_changed)

        # Connect to profile switching (signal from main window or profile manager)
        if on_profile_changed_signal is not None:
            on_profile_changed_signal.connect(self.on_profile_switched)

        # Initial load
        self.update_profile_header()
        self.load_scans()

    def on_profile_switched(self):
        profile = self.get_current_profile_func()
        is_guest = self.is_guest_profile(profile)
        self.update_for_guest_profile(is_guest)
        if not is_guest:
            self.update_profile_header()
            self.load_scans()
        else:
            self.header_label.setText("Guest Scan History")
            self.scan_table.setRowCount(0)
            self.scan_table.setVisible(False)
            self.delete_selected_btn.setVisible(False)
            self.guest_disclaimer.setVisible(True)

    @staticmethod
    def is_guest_profile(profile) -> bool:
        return profile and profile.get("id") == "guest"

    def update_for_guest_profile(self, is_guest: bool):
        if is_guest:
            self.scan_table.setVisible(False)
            self.delete_selected_btn.setVisible(False)
            self.guest_disclaimer.setVisible(True)
        else:
            self.scan_table.setVisible(True)
            self.guest_disclaimer.setVisible(False)

    def update_profile_header(self):
        profile = self.get_current_profile_func()
        if profile:
            name = profile.get("name", "Profile")
        else:
            name = "Profile"
        self.current_profile = profile
        self.header_label.setText(f"{name}'s Scan History")
        self.load_scans()

    def load_scans(self):
        if self.is_guest_profile(self.current_profile):
            self.scan_table.setRowCount(0)
            self.delete_selected_btn.setVisible(False)
            self.guest_disclaimer.setVisible(True)
            return

        self.scan_table.setRowCount(0)
        self.scan_data = []
        self.delete_selected_btn.setVisible(False)
        if not self.current_profile:
            return

        profile_id = self.current_profile.get('id', self.current_profile.get('name', 'default'))
        scan_dir = os.path.join("profile_scans", str(profile_id))
        scans_json = os.path.join(scan_dir, "scans.json")
        if os.path.exists(scans_json):
            with open(scans_json, "r") as f:
                scans = json.load(f)
            self.scan_data = scans
            for i, scan in enumerate(scans):
                self.add_scan_row(i, scan)
        else:
            self.scan_table.setRowCount(1)
            self.scan_table.setItem(0, 0, QTableWidgetItem("No scans found."))
            for col in range(1, self.scan_table.columnCount()):
                self.scan_table.setItem(0, col, QTableWidgetItem(""))

    def add_scan_row(self, row_idx, scan):
        self.scan_table.insertRow(row_idx)

        # 0: Date/Time
        ts = scan.get('timestamp', '')
        date_str = self.format_scan_timestamp(ts)
        self.scan_table.setItem(row_idx, 0, QTableWidgetItem(date_str))

        # 1: Body Part
        body_part = scan.get('body_part', '')
        # Defensive: if value is None, force to empty string
        if body_part is None:
            body_part = ''
        self.scan_table.setItem(row_idx, 1, QTableWidgetItem(str(body_part)))

        # 2: Melanoma %
        mel_percent = self.extract_melanoma_percent(scan.get('melanoma_likelihood', ''))
        self.scan_table.setItem(row_idx, 2, QTableWidgetItem(mel_percent))

        # 3: Risk level (High/Moderate/Low)
        risk_level = self.get_risk_level(mel_percent)
        risk_item = QTableWidgetItem(risk_level)
        risk_item.setTextAlignment(Qt.AlignCenter)
        if risk_level == "High":
            risk_item.setForeground(Qt.red)
        elif risk_level == "Moderate":
            risk_item.setForeground(Qt.darkYellow)
        else:
            risk_item.setForeground(Qt.green)
        self.scan_table.setItem(row_idx, 3, risk_item)

        # 4: Image thumbnail
        img_item = QTableWidgetItem()
        img_path = scan.get('image_path', '')
        if img_path and os.path.exists(img_path):
            pix = QPixmap(img_path).scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            img_item.setIcon(QIcon(pix))
        self.scan_table.setItem(row_idx, 4, img_item)

        # 5: Delete button
        del_btn = QPushButton("Delete")
        del_btn.setStyleSheet("background:#ff5a5a; color:#fff; border:none; border-radius:9px; font-weight:bold;")
        # Use lambda with current row index (do not use partial or row_idx directly, as it may change)
        del_btn.clicked.connect(lambda _, r=row_idx: self.delete_scan(r))
        self.scan_table.setCellWidget(row_idx, 5, del_btn)

        # DEBUG
        # print(f"Added scan row {row_idx}: ts={date_str} body_part={body_part} melanoma={mel_percent} risk={risk_level} img={img_path}")

        # Make sure each cell is never None
        for col in range(6):
            if not self.scan_table.item(row_idx, col):
                self.scan_table.setItem(row_idx, col, QTableWidgetItem(""))




    def on_selection_changed(self, selected, deselected):
        # Show button only if 2 or more rows are selected (not in guest mode)
        if self.is_guest_profile(self.current_profile):
            self.delete_selected_btn.setVisible(False)
            return
        selected_rows = self.scan_table.selectionModel().selectedRows()
        self.delete_selected_btn.setVisible(len(selected_rows) > 1)

    def handle_table_click(self, row, col):
        # If you want clicking the image cell to pop up a full image, do it here
        if col == 4:
            scan = self.scan_data[row]
            img_path = scan.get('image_path', '')
            if img_path and os.path.exists(img_path):
                d = QDialog(self)
                d.setWindowTitle("Scan Image")
                l = QLabel()
                l.setPixmap(QPixmap(img_path).scaled(380, 380, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                lay = QVBoxLayout(d)
                lay.addWidget(l)
                d.exec_()

    def delete_scan_by_key(self, timestamp, body_part):
        """Delete scan by unique identifier (timestamp + body part) to avoid row index mismatches."""
        if self.is_guest_profile(self.current_profile):
            return
        idx = next((i for i, scan in enumerate(self.scan_data)
                    if scan.get('timestamp', '') == timestamp and scan.get('body_part', '') == body_part), None)
        if idx is None:
            return
        reply = QMessageBox.question(
            self, "Confirm Delete", "Are you sure you want to delete this scan?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            del self.scan_data[idx]
            self.save_scan_data()
            self.load_scans()
            QMessageBox.information(self, "Deleted", "Scan deleted successfully.")

    def delete_selected_scans(self):
        if self.is_guest_profile(self.current_profile):
            return
        selected_rows = set(idx.row() for idx in self.scan_table.selectionModel().selectedRows())
        if not selected_rows:
            QMessageBox.information(self, "No Selection", "Please select one or more scans to delete.")
            return
        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to delete {len(selected_rows)} selected scan(s)?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return
        # Remove from highest to lowest index to avoid shifting
        for row_idx in sorted(selected_rows, reverse=True):
            if row_idx < len(self.scan_data):
                del self.scan_data[row_idx]
        self.save_scan_data()
        self.load_scans()
        QMessageBox.information(self, "Deleted", "Selected scan(s) deleted successfully.")

    def save_scan_data(self):
        """Save current scan_data to file."""
        if not self.current_profile or self.is_guest_profile(self.current_profile):
            return
        profile_id = self.current_profile.get('id', self.current_profile.get('name', 'default'))
        scan_dir = os.path.join("profile_scans", str(profile_id))
        # Ensure the directory exists before saving
        os.makedirs(scan_dir, exist_ok=True)
        scans_json = os.path.join(scan_dir, "scans.json")
        with open(scans_json, "w") as f:
            json.dump(self.scan_data, f, indent=2)

    def on_rows_moved(self, parent, start, end, dest, dest_row):
        """Handles saving the new order after drag-and-drop."""
        if self.is_guest_profile(self.current_profile):
            return
        # Rebuild scan_data from table order
        new_order = []
        for row in range(self.scan_table.rowCount()):
            timestamp = self.scan_table.item(row, 0).text()
            body_part = self.scan_table.item(row, 1).text()
            match = next((s for s in self.scan_data
                          if self.format_scan_timestamp(s.get('timestamp', '')) == timestamp and
                          s.get('body_part', '') == body_part), None)
            if match:
                new_order.append(match)
        self.scan_data = new_order
        self.save_scan_data()

    def save_scan_order(self, scans):
        """Explicit save (used by sort functions)."""
        if not self.is_guest_profile(self.current_profile):
            self.scan_data = scans
            self.save_scan_data()

    @staticmethod
    def extract_melanoma_percent(html_str):
        # If already a number, just return as string
        if isinstance(html_str, (int, float)):
            return f"{html_str:.1f}"
        # Otherwise, try to extract from string with percent
        match = re.search(r'(\d+(\.\d+)?)%', str(html_str))
        if match:
            return match.group(1)
        # Fallback: try to convert directly
        try:
            return f"{float(html_str):.1f}"
        except Exception:
            return ""

    @staticmethod
    def get_risk_level(mel_percent):
        try:
            percent = float(mel_percent)
        except Exception:
            percent = 0
        if percent > 50:
            return "High"
        elif percent > 30:
            return "Moderate"
        else:
            return "Low"

    @staticmethod
    def format_scan_timestamp(ts_string):
        try:
            dt = datetime.strptime(ts_string, "%Y%m%d_%H%M%S")
            formatted = dt.strftime("%-d/%-m/%Y, %-I:%M %p") if hasattr(dt, 'strftime') else dt.strftime("%d/%m/%Y, %I:%M %p").replace('/0', '/').lstrip('0')
            return formatted
        except Exception:
            return ts_string

