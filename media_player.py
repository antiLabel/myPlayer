# media_player.py
import mpv
from PySide6.QtCore import QObject, Signal
import locale
locale.setlocale(locale.LC_NUMERIC, 'C')

class MediaPlayerService(QObject):
    playback_finished = Signal()
    position_changed = Signal(int)
    duration_changed = Signal(int)
    playback_state_changed = Signal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._player = mpv.MPV(
            vo='libmpv',
            msg_level = "all=no",
            log_handler=print # 打印MPV的日志，方便调试
        )
        self._player.observe_property('time-pos', self.on_position_changed)
        self._player.observe_property('duration', self.on_duration_changed)
        self._player.observe_property('pause', self.on_pause_state_changed)

    def get_player_handle(self):
        """返回 mpv 实例，供 MPVWidget 使用"""
        return self._player

    def set_media(self, file_path: str):
        self._player.play(file_path)
        self._player.pause = False
        
    def close(self):
        """安全终止播放器"""
        self._player.terminate()

    # --- 属性观察回调函数 ---
    def on_position_changed(self, name, value):
        if value is not None:
            self.position_changed.emit(int(value * 1000))

    def on_duration_changed(self, name, value):
        if value is not None:
            self.duration_changed.emit(int(value * 1000))

    def on_pause_state_changed(self, name, is_paused):
        if is_paused is not None:
            self.playback_state_changed.emit(not is_paused)

    
    def on_end_file(event):
        # 3. 在事件发生时，发射我们的自定义信号
        print("MediaPlayerService: Detected end-file event.")
        self.playback_finished.emit()