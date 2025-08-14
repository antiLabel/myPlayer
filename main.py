import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QFileDialog

from media_widgets import PlayerUI
from media_player import MediaPlayerService
from qt_material import apply_stylesheet
import os
from iconmanager.icon_manager import IconManager

class VideoPlayerWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MPV视频播放器 v1.1")
        self.theme = 'dark_teal.xml'
        self._set_stylesheet()
        self.dir_path = os.path.dirname(os.path.abspath(__file__)) 
        icon_path = os.path.join(self.dir_path, 'icons')
        self.icon_manager = IconManager(self.theme, icon_path)

        self.media_player_service = MediaPlayerService()
        self.ui = PlayerUI(self.icon_manager, self)
        self.setCentralWidget(self.ui)
        self._set_menu_bar()
        self.statusBar().showMessage("准备就绪")
        
        self.media_player_service.set_video_widget(self.ui.video_frame)

        self.connect_signals()

    def _set_stylesheet(self):
        apply_stylesheet(
            QApplication.instance(), self.theme
            )
        
    def connect_signals(self):
        # 播放控制
        self.ui.play_button.clicked.connect(self.media_player_service.play_pause)
        self.media_player_service.playback_state_changed.connect(self.ui.update_play_button_icon)

        # 进度控制
        self.ui.slider.sliderMoved.connect(self.media_player_service.set_position)
        self.media_player_service.position_changed.connect(self.ui.update_slider_position)
        self.media_player_service.duration_changed.connect(self.ui.set_slider_range)
        

        self.ui.volume_slider.valueChanged.connect(self.media_player_service.set_volume)
        self.media_player_service.volume_changed.connect(self.ui.update_volume_slider)
        
        self.ui.mute_button.clicked.connect(self.media_player_service.toggle_mute)
        self.media_player_service.mute_changed.connect(self.ui.update_mute_button_icon)


    def _set_menu_bar(self):
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("文件")
        
        open_action = file_menu.addAction("打开视频")
        open_action.setStatusTip("打开视频文件")
        open_action.setIcon(self.icon_manager.get_add_icon())
        open_action.triggered.connect(self.open_file)


    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "打开视频", "", "所有文件 (*.*)")
        if file_path:
            self.media_player_service.set_media(file_path)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VideoPlayerWindow()
    window.resize(800, 600)
    window.show()
    sys.exit(app.exec())