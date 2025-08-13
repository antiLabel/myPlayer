# widgets.py - 视图层 (View)
# 这个文件与 vlc 版本完全相同，无需任何改动。
# 这完美地展示了将业务逻辑与UI分离的好处。

from PySide6.QtWidgets import QWidget, QPushButton, QSlider, QHBoxLayout, QVBoxLayout, QStyle
from PySide6.QtCore import Qt

class PlayerUI(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # 我们仍然使用一个通用的 QWidget 作为视频“画板”
        self.video_frame = QWidget()
        self.video_frame.setStyleSheet("background-color: black;")
        
        self.open_button = QPushButton()
        self.open_button.setIcon(self.style().standardIcon(QStyle.SP_DirOpenIcon))
        self.open_button.setToolTip("打开文件")

        self.play_button = QPushButton()
        self.play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.play_button.setToolTip("播放")

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0, 0)

        control_layout = QHBoxLayout()
        control_layout.addWidget(self.open_button)
        control_layout.addWidget(self.play_button)
        control_layout.addWidget(self.slider)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.video_frame)
        main_layout.addLayout(control_layout)

        self.setLayout(main_layout)

    def set_slider_range(self, duration: int):
        self.slider.setRange(0, duration)

    def update_slider_position(self, position: int):
        if not self.slider.isSliderDown():
            self.slider.setValue(position)

