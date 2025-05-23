import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QTabWidget, QVBoxLayout
from PyQt5.QtCore import pyqtSignal, QObject
from ProfileManager import ProfileManager
from ScanView import ScanView
from MonitorTab import MonitorTab
from InfoView import InfoView
from SettingsDialogue import SettingsDialogue

class SignalBus(QObject):
    profile_changed = pyqtSignal()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Melanoma Detection & Observation")
        self.setMinimumSize(1100, 720)
        self.current_profile = None
        self.signals = SignalBus()

        self.monitor_tab = MonitorTab(self.get_current_profile, on_profile_changed_signal=self.signals.profile_changed)

        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.North)
        layout.addWidget(self.tabs)

        # Tabs - constructed with central profile support
        self.profile_manager = ProfileManager(on_profile_changed=self.set_current_profile)
        self.tabs.addTab(self.profile_manager, "Profiles")

        self.scan_view = ScanView(get_current_profile_func=self.get_current_profile)
        self.tabs.addTab(self.scan_view, "Scan")

        self.monitor_tab = MonitorTab(get_current_profile_func=self.get_current_profile)
        self.tabs.addTab(self.monitor_tab, "Monitor")

        self.info_view = InfoView()
        self.tabs.addTab(self.info_view, "About")

        self.settings_dialogue = SettingsDialogue()
        self.tabs.addTab(self.settings_dialogue, "Settings")

        # After all tabs exist, load profiles to avoid callback errors
        self.profile_manager.load_profiles()

    def get_current_profile(self):
        return self.current_profile

    def set_current_profile(self, profile):
        self.current_profile = profile
        # Update monitor/scanner as needed
        if hasattr(self, "monitor_tab") and self.monitor_tab:
            self.monitor_tab.update_profile_header()
        if hasattr(self, "scan_view") and self.scan_view:
            if profile:
                name = profile.get("name", "")
                self.scan_view.instructions.setText(
                    f"<b>Current Profile:</b> {name}<br>"
                    "<b>Step 1:</b> Click the body map to select a body part.<br>"
                    "<b>Step 2:</b> Upload a lesion photo for analysis."
                )
            else:
                self.scan_view.instructions.setText(
                    "<b>Step 1:</b> Click the body map to select a body part.<br>"
                    "<b>Step 2:</b> Upload a lesion photo for analysis."
                )
        self.signals.profile_changed.emit()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle("Fusion")  # Optional: looks better cross-platform!
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
