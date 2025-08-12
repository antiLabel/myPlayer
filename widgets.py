# widgets.py - 视图层 (View)
# 职责：定义所有UI组件和它们的布局。它不包含任何复杂的业务逻辑。

from PySide6.QtWidgets import QWidget, QPushButton, QSlider, QHBoxLayout, QVBoxLayout, QStyle
from PySide6.QtCore import Qt
from PySide6.QtMultimediaWidgets import QVideoWidget

class PlayerUI(QWidget):
    """
    这个类是播放器的“仪表盘”。它只负责创建和摆放按钮、进度条等控件。
    它接收一个 QVideoWidget 用于显示视频画面。
    """
    def __init__(self, video_widget: QVideoWidget, parent=None):
        super().__init__(parent)

        # --- 创建控件 ---
        self.video_widget = video_widget # 视频画面

        # 打开文件按钮
        self.open_button = QPushButton()
        self.open_button.setIcon(self.style().standardIcon(QStyle.SP_DirOpenIcon))
        self.open_button.setToolTip("打开文件")

        # 播放/暂停按钮
        self.play_button = QPushButton()
        self.play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.play_button.setToolTip("播放")

        # 进度条
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0, 0) # 初始范围为0

        # --- 设置布局 ---
        # 控制按钮的水平布局
        control_layout = QHBoxLayout()
        control_layout.addWidget(self.open_button)
        control_layout.addWidget(self.play_button)
        control_layout.addWidget(self.slider)

        # 主垂直布局
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.video_widget) # 视频画面在上方
        main_layout.addLayout(control_layout)   # 控制栏在下方

        self.setLayout(main_layout)

    # --- 定义一些供Controller调用的槽函数 ---
    def set_slider_range(self, duration: int):
        """设置进度条的最大值"""
        self.slider.setRange(0, duration)

    def update_slider_position(self, position: int):
        """更新进度条的当前位置"""
        self.slider.setValue(position)

