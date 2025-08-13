# main.py - 控制层 (Controller) 和应用入口
# 这个文件也与 vlc 版本完全相同，无需任何改动。
# Controller 只关心 MediaPlayerService 暴露的信号和槽，
# 它完全不知道底层引擎已经从 VLC 换成了 MPV。

import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QFileDialog, QStyle

from widgets import PlayerUI
from media_player import MediaPlayerService

class VideoPlayerWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MPV 视频播放器 MVP")

        self.media_player_service = MediaPlayerService()
        self.ui = PlayerUI()
        self.setCentralWidget(self.ui)
        
        # 核心集成步骤：将UI的画板传递给服务层
        self.media_player_service.set_video_widget(self.ui.video_frame)

        self.connect_signals()

    def connect_signals(self):
        self.ui.open_button.clicked.connect(self.open_file)
        self.ui.play_button.clicked.connect(self.media_player_service.play_pause)
        
        self.media_player_service.position_changed.connect(self.ui.update_slider_position)
        self.media_player_service.duration_changed.connect(self.ui.set_slider_range)
        
        self.ui.slider.sliderMoved.connect(self.media_player_service.set_position)
        
        self.media_player_service.playback_state_changed.connect(self.update_play_button_icon)

    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "打开视频", "", "所有文件 (*.*)")
        if file_path:
            self.media_player_service.set_media(file_path)
            # mpv 加载后会自动播放，所以这里不需要再调用 play_pause

    def update_play_button_icon(self, is_playing: bool):
        if is_playing:
            self.ui.play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
        else:
            self.ui.play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VideoPlayerWindow()
    window.resize(800, 600)
    window.show()
    sys.exit(app.exec())
