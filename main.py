# main.py
import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QFileDialog
from PySide6.QtCore import Slot # 导入 Slot

from media_player import MediaPlayerService
from mpv_widget import MPVWidget
from set_default_gl_format import enable_debug_gl_default_format

class VideoPlayerWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("第一步验证：MPV 渲染核心")

        self.media_player_service = MediaPlayerService()
        self.mpv_widget = MPVWidget(self.media_player_service)
        
        self.setCentralWidget(self.mpv_widget)
        
        self._set_menu_bar()
        self.connect_signals()


    def _set_menu_bar(self):
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("文件")
        open_action = file_menu.addAction("打开视频")
        open_action.triggered.connect(self.open_file)

    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "打开视频", ".", "视频文件 (*.mp4 *.mkv *.avi)")
        if file_path:

            if self.mpv_widget.ctx:
                self.media_player_service.set_media(file_path)
    
    def connect_signals(self):
        # 2. 新增连接：当播放结束时，调用 mpv_widget 的 disable_updates 方法
        self.media_player_service.playback_finished.connect(self.mpv_widget.disable_updates)

    def closeEvent(self, event):
        self.media_player_service.close()
        super().closeEvent(event)

if __name__ == "__main__":
    enable_debug_gl_default_format()
    app = QApplication(sys.argv)
    window = VideoPlayerWindow()
    window.resize(800, 600)
    window.show()
    sys.exit(app.exec())