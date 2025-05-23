from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton, QTextBrowser
from PyQt5.QtCore import Qt

class InfoView(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 18)
        layout.setSpacing(18)

        # App title
        title = QLabel("<h2 style='color:#22b6b2;'>Melanoma Detection & Observation</h2>")
        layout.addWidget(title, alignment=Qt.AlignLeft)

        # Tagline / quick description
        desc = QLabel(
            "<b>About this tool:</b><br>"
            "This application allows you to <b>detect, observe, and track</b> potential melanoma and other skin lesions. "
            "It helps you record images and estimate risk over time, making it easier to notice changes and take early action.<br><br>"
            "<span style='color:#e34a6f;font-weight:bold;'>Note:</span> <b>This tool does NOT replace clinical diagnosis.</b> "
            "If a result shows high risk, or you are unsure about a lesion, <b>please see your doctor or dermatologist.</b>"
        )
        desc.setWordWrap(True)
        layout.addWidget(desc)

        # Privacy reassurance
        privacy = QLabel(
            "<span style='color:#22b6b2;font-weight:bold;'>Privacy:</span> "
            "All data is stored locally on your device. No information leaves your computer unless you choose to export or share."
        )
        privacy.setWordWrap(True)
        layout.addWidget(privacy)

        # How to use (bulleted)
        instructions = QLabel(
            "<b>How to use:</b>"
            "<ul>"
            "<li>Select or create your profile.</li>"
            "<li>In the <b>Scan</b> tab, click the body map (front or back) to mark a lesion's location.</li>"
            "<li>Upload a clear, focused photo of the skin lesion.</li>"
            "<li>Review the detection results, and save them to your profile for future comparison.</li>"
            "<li>In the <b>Monitor</b> tab, you can track all saved scans and spot changes over time.</li>"
            "</ul>"
        )
        instructions.setWordWrap(True)
        layout.addWidget(instructions)

        # FAQ (simple)
        faq_label = QLabel("<b>Frequently Asked Questions</b>")
        layout.addWidget(faq_label)
        faq = QTextBrowser()
        faq.setOpenExternalLinks(True)
        faq.setHtml(
            "<b>Q: Is this a replacement for a doctor?</b><br>"
            "A: <b>No.</b> This tool helps you track and notice changes but cannot provide a medical diagnosis. "
            "Always consult a healthcare professional for suspicious or changing lesions.<br><br>"
            "<b>Q: What happens to my photos and scans?</b><br>"
            "A: Everything stays on your device unless you export it. No cloud or remote storage is used by default.<br><br>"
            "<b>Q: How do I get more help?</b><br>"
            "A: See the <a href='https://www.cancer.org.au/cancer-information/types-of-cancer/skin-cancer'>Cancer Council</a> or <a href='https://www.melanoma.org.au/'>Melanoma Institute Australia</a> for more information."
        )
        faq.setMaximumHeight(220)
        layout.addWidget(faq)

        # Feedback button (example; could link to email or github)
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        self.feedback_btn = QPushButton("Send Feedback")
        self.feedback_btn.setToolTip("Let us know how we can improve this app!")
        self.feedback_btn.clicked.connect(self.on_feedback)
        btn_row.addWidget(self.feedback_btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        layout.addStretch(1)

    def on_feedback(self):
        import webbrowser
        # Open a mailto: link or project page
        webbrowser.open("mailto:support@example.com?subject=Melanoma%20Detection%20App%20Feedback")
