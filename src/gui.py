from PyQt5.QtWidgets import (
    QMainWindow, QTabWidget, QStatusBar, QAction, QToolBar, QLabel, QWidget, QHBoxLayout, QVBoxLayout
)
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt
from ScanView import ScanView
from MonitorTab import MonitorTab
from ProfileManager import ProfileManager
from InfoView import InfoView
from SettingsDialogue import SettingsDialogue
import os
from utils import resource_path

ICON_HEALTH = resource_path(os.path.join("Resources", "icon_health.png"))  # add these icons in resources/
ICON_PEOPLE = resource_path(os.path.join("Resources", "icon_people.png"))
ICON_HISTORY = resource_path(os.path.join("Resources", "icon_history.png"))
ICON_INFO = resource_path(os.path.join("Resources", "icon_info.png"))
ICON_SETTINGS = resource_path(os.path.join("Resources", "icon_settings.png"))

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Melanoma Detection & Observation Tool — Empowering Health for All")
        self.resize(1200, 800)
        self.setMinimumSize(950, 650)

        # --- Top toolbar with icons and tooltips ---
        self.toolbar = QToolBar()
        self.toolbar.setMovable(False)
        self.addToolBar(self.toolbar)
        self.toolbar.setStyleSheet("QToolBar { background: #f9fbfd; border: none; }")

        info_action = QAction(QIcon(ICON_INFO), "Information", self)
        info_action.setToolTip("About & help (opens information window)")
        info_action.triggered.connect(self.show_info)
        self.toolbar.addAction(info_action)

        settings_action = QAction(QIcon(ICON_SETTINGS), "Settings", self)
        settings_action.setToolTip("Adjust app preferences")
        settings_action.triggered.connect(self.show_settings)
        self.toolbar.addAction(settings_action)

        # --- Central widget: Main tabs with icons and large clickable areas ---
        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.North)
        self.tabs.setMovable(False)
        self.tabs.setElideMode(Qt.ElideNone)
        self.tabs.setDocumentMode(True)
        self.tabs.setStyleSheet("QTabWidget::pane { border-top: 2px solid #22b6b2; }")

        self.scan_view = ScanView()
        self.monitor_tab = MonitorTab()
        self.profile_manager = ProfileManager()

        self.tabs.addTab(self.scan_view, QIcon(ICON_HEALTH), "Scan")
        self.tabs.setTabToolTip(0, "Scan a new skin lesion, assess risk, and track on the body map.")
        self.tabs.addTab(self.monitor_tab, QIcon(ICON_HISTORY), "Monitor")
        self.tabs.setTabToolTip(1, "Monitor history and progress of observed lesions.")
        self.tabs.addTab(self.profile_manager, QIcon(ICON_PEOPLE), "Profiles")
        self.tabs.setTabToolTip(2, "Manage user profiles and health data.")

        self.setCentralWidget(self.tabs)

        # --- Status bar: Persistent information and feedback ---
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.update_status("Welcome! Start by scanning a lesion or viewing your monitoring history.")

        # --- Info and Settings dialogs ---
        self.info_view = InfoView(self)
        self.settings_dialogue = SettingsDialogue(self)

        # --- Optional: Welcome banner for inclusivity & onboarding (only on first load) ---
        self.welcome_banner = QLabel()
        self.welcome_banner.setText(
            "<h2>Welcome to Melanoma Detection & Observation!</h2>"
            "<p>This tool empowers everyone to assess and track skin health over time.<br>"
            "Use the <b>Scan</b> tab to begin a new assessment.<br>"
            "All information is stored securely and privately.</p>"
        )
        self.welcome_banner.setAlignment(Qt.AlignCenter)
        self.welcome_banner.setStyleSheet(
            "background: #e6f9f8; color: #11364d; border-radius: 18px; padding: 20px; font-size: 18px; margin: 30px;"
        )
        self.set_welcome_banner_visible(True)
        self.tabs.currentChanged.connect(self._hide_welcome_on_tab_change)

    def set_welcome_banner_visible(self, visible):
        if visible:
            # Add banner as an overlay to the Scan tab (first tab) if it is empty
            if not hasattr(self, "_banner_added"):
                main_layout = self.scan_view.layout()
                main_layout.insertWidget(0, self.welcome_banner)
                self._banner_added = True
        else:
            if hasattr(self, "_banner_added") and self._banner_added:
                self.welcome_banner.hide()

    def _hide_welcome_on_tab_change(self, idx):
        # Hide welcome banner once user interacts with other tabs
        self.set_welcome_banner_visible(False)

    def show_info(self):
        self.info_view.show()

    def show_settings(self):
        self.settings_dialogue.exec_()

    def update_status(self, message):
        self.status_bar.showMessage(message, 8000)
