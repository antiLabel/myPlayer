import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QFileDialog, QStyle
from PySide6.QtCore import QUrl

# 从我们的视图层导入UI定义
from widgets import PlayerUI
# 从我们的模型/服务层导入播放器逻辑
from media_player import MediaPlayerService

class VideoPlayerWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("简易视频播放器 MVP")

        # 1. 初始化模型/服务层
        self.media_player_service = MediaPlayerService()

        # 2. 初始化视图层
        # 将 media_player_service 实例传递给UI层，以便UI可以控制它
        self.ui = PlayerUI(self.media_player_service.get_video_widget())
        self.setCentralWidget(self.ui)

        # 3. 连接信号与槽 (这是Controller的核心职责)
        self.connect_signals()

    def connect_signals(self):
        """将UI发出的信号连接到处理函数(槽)上"""
        # 文件操作
        self.ui.open_button.clicked.connect(self.open_file)

        # 播放控制
        self.ui.play_button.clicked.connect(self.media_player_service.play_pause)

        # 进度条与播放位置同步
        # a. 当播放器位置改变时，更新进度条
        self.media_player_service.position_changed.connect(self.ui.update_slider_position)
        # b. 当视频总时长可用时，设置进度条范围
        self.media_player_service.duration_changed.connect(self.ui.set_slider_range)
        # c. 当用户拖动进度条时，更新播放器位置
        self.ui.slider.sliderMoved.connect(self.media_player_service.set_position)

        # 监听播放状态的变化，以更新播放/暂停按钮的图标
        self.media_player_service.playback_state_changed.connect(self.update_play_button_icon)

    def open_file(self):
        """打开视频文件"""
        file_path, _ = QFileDialog.getOpenFileName(self, "打开视频", "", "视频文件 (*.mp4 *.flv *.mov *.avi)")
        if file_path:
            self.media_player_service.set_media(QUrl.fromLocalFile(file_path))
            # 加载后自动播放
            self.media_player_service.play_pause()

    def update_play_button_icon(self, state):
        """根据播放状态更新播放按钮的图标"""
        if state == MediaPlayerService.PlayingState:
            self.ui.play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
        else:
            self.ui.play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VideoPlayerWindow()
    window.resize(800, 600)
    window.show()
    sys.exit(app.exec())