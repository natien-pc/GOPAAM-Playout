import json
import os
from PyQt5.QtWidgets import QMainWindow, QLabel, QWidget, QVBoxLayout, QPushButton, QFileDialog, QListWidget, QHBoxLayout
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QPixmap, QImage
from player import VideoPlayer
from overlays import OverlayManager
from rss_reader import RSSReader
from sms_moderation import SMSModeration

from utils import cvframe_to_qimage

PROJECT_ROOT = os.path.dirname(__file__)
LAYOUT_FILE = os.path.join(PROJECT_ROOT, "layout.json")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GOPAAM Playout + CG (starter)")
        self.resize(1280, 720)

        self.video_label = QLabel()
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setStyleSheet("background-color: black;")
        self.status = QLabel("Stopped")

        self.open_btn = QPushButton("Open Video/Stream")
        self.open_btn.clicked.connect(self.open_file)

        self.play_btn = QPushButton("Play/Pause")
        self.play_btn.clicked.connect(self.toggle_play)

        self.sms_list = QListWidget()
        self.sms_moderation = SMSModeration()
        self.sms_list.addItems(self.sms_moderation.preview_items())

        top = QHBoxLayout()
        top.addWidget(self.open_btn)
        top.addWidget(self.play_btn)
        top.addWidget(self.status)

        right = QVBoxLayout()
        right.addWidget(QLabel("SMS Queue"))
        right.addWidget(self.sms_list)
        approve = QPushButton("Approve Selected")
        approve.clicked.connect(self.approve_selected)
        right.addWidget(approve)

        layout = QVBoxLayout()
        layout.addLayout(top)
        layout.addWidget(self.video_label)

        container = QWidget()
        container.setLayout(layout)

        main_layout = QHBoxLayout()
        main_layout.addWidget(container, 4)
        right_widget = QWidget()
        right_widget.setLayout(right)
        main_layout.addWidget(right_widget, 1)

        main = QWidget()
        main.setLayout(main_layout)
        self.setCentralWidget(main)

        # Video system
        self.player = VideoPlayer()
        self.player.set_frame_callback(self.on_frame)

        # Overlays
        self.overlay_manager = OverlayManager()
        self.load_layout(LAYOUT_FILE)

        # Refresh timer for GUI (for overlays that tick)
        self.gui_timer = QTimer()
        self.gui_timer.setInterval(100)  # 10 fps UI updates for overlays
        self.gui_timer.timeout.connect(self.overlay_manager.tick)
        self.gui_timer.start()

    def load_layout(self, path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                cfg = json.load(f)
            self.overlay_manager.configure_from_layout(cfg.get("overlays", []))
            self.status.setText("Layout loaded")
        except Exception as e:
            self.status.setText(f"Layout load failed: {e}")

    def open_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open video or stream", "", "Video files (*.mp4 *.avi *.mkv);;All files (*)")
        if path:
            self.player.open(path)
            self.status.setText(f"Opened {path}")

    def toggle_play(self):
        if self.player.is_playing():
            self.player.pause()
            self.play_btn.setText("Play")
            self.status.setText("Paused")
        else:
            self.player.play()
            self.play_btn.setText("Pause")
            self.status.setText("Playing")

    def on_frame(self, frame):
        # Called in player thread context; frame is BGR numpy array.
        # Compose overlays on top
        composed = self.overlay_manager.render(frame)
        qimg = cvframe_to_qimage(composed)
        pix = QPixmap.fromImage(qimg)
        self.video_label.setPixmap(pix.scaled(self.video_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def approve_selected(self):
        for item in self.sms_list.selectedItems():
            text = item.text()
            self.sms_moderation.approve(text)
            self.sms_list.takeItem(self.sms_list.row(item))

    def closeEvent(self, event):
        self.player.stop()
        event.accept()