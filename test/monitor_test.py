import sys
import os
import pytest
import json
from PyQt5.QtWidgets import QApplication, QPushButton, QMessageBox
from PyQt5.QtCore import Qt

# Allow test to run regardless of working directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from MonitorTab import MonitorTab

@pytest.fixture(scope="session")
def app():
    """Create a QApplication only once for all GUI tests."""
    return QApplication([])

@pytest.fixture
def test_profile(tmp_path):
    # Simulate a non-guest profile
    profile = {"id": "test123", "name": "Test User"}
    scan_dir = tmp_path / "profile_scans" / "test123"
    scan_dir.mkdir(parents=True, exist_ok=True)
    # Example scan
    scans = [{
        "timestamp": "20240415_101010",
        "body_part": "Chest",  # Changed from "Chest (Front)"
        "melanoma_likelihood": "85.0%",
        "image_path": "",
    }]
    with open(scan_dir / "scans.json", "w") as f:
        json.dump(scans, f)
    return profile, str(scan_dir)


@pytest.fixture
def guest_profile():
    return {"id": "guest", "name": "Guest"}

@pytest.fixture
def monitor_tab(app, test_profile, monkeypatch):
    profile, scan_dir = test_profile
    def get_current_profile():
        return profile
    original_join = os.path.join
    def patched_join(*args):
        # Only replace first "profile_scans" call
        if args and args[0] == "profile_scans":
            return original_join(scan_dir, *args[1:])
        return original_join(*args)
    monkeypatch.setattr(os.path, "join", patched_join)
    return MonitorTab(get_current_profile)


def test_guest_profile_hides_table(app, guest_profile, monkeypatch):
    def get_current_profile():
        return guest_profile
    tab = MonitorTab(get_current_profile)
    tab.show()
    app.processEvents()
    tab.on_profile_switched()
    assert not tab.scan_table.isVisible()
    assert tab.guest_disclaimer.isVisible()


def test_extract_melanoma_percent():
    assert MonitorTab.extract_melanoma_percent("85.3%") == "85.3"

def test_get_risk_level():
    assert MonitorTab.get_risk_level("90") == "High"

def test_format_scan_timestamp():
    assert "2024" in MonitorTab.format_scan_timestamp("20240415_101010")
    assert MonitorTab.format_scan_timestamp("notadate") == "notadate"
