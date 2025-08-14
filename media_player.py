import mpv
from PySide6.QtCore import QObject, Signal

class MediaPlayerService(QObject):
    # 接口契约
    position_changed = Signal(int)
    duration_changed = Signal(int)
    playback_state_changed = Signal(bool)
    volume_changed = Signal(int)
    mute_changed = Signal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        
        self._player = mpv.MPV(input_default_bindings=True, input_vo_keyboard=True)
        self._player.pause = True
        
        # 观察核心属性
        self._player.observe_property('time-pos', self.on_position_changed)
        self._player.observe_property('duration', self.on_duration_changed)
        self._player.observe_property('pause', self.on_pause_state_changed)
        self._player.observe_property('volume', self.on_volume_changed)
        self._player.observe_property('mute', self.on_mute_changed)

    def set_video_widget(self, widget):
        self._player.wid = widget.winId()

    def set_media(self, file_path: str):
        self._player.play(file_path)
        self._player.pause = False

    def play_pause(self):
        self._player.pause = not self._player.pause

    def set_position(self, position_ms: int):
        position_sec = position_ms / 1000.0
        self._player.time_pos = position_sec

    def set_volume(self, volume: int):
        """设置音量，范围 0-100"""
        self._player.volume = volume
        
    def toggle_mute(self):
        """切换静音状态"""
        self._player.mute = not self._player.mute

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
            

    def on_volume_changed(self, name, value):
        if value is not None:
            self.volume_changed.emit(int(value))
            
    def on_mute_changed(self, name, value):
        if value is not None:
            self.mute_changed.emit(value)