# media_player.py - 模型/服务层 (mpv-python版)
# 职责：封装所有与 mpv 相关的核心功能，并利用其属性观察者来驱动Qt信号。

import mpv
from PySide6.QtCore import QObject, Signal

class MediaPlayerService(QObject):
    """
    这是基于 mpv 的新引擎。它利用了 mpv 强大的属性驱动 API。
    我们不再需要手动桥接事件，而是“观察”我们关心的属性，当它们变化时自动触发函数。
    """
    # 接口契约保持不变：对外暴露的信号和上个版本完全一样
    position_changed = Signal(int)
    duration_changed = Signal(int)
    playback_state_changed = Signal(bool) # True for playing, False for not playing

    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 1. 初始化 MPV 实例
        # input_default_bindings 和 input_vo_keyboard 设为 no
        # 可以阻止 mpv 默认的快捷键行为，让我们的PySide窗口全权处理键盘事件
        self._player = mpv.MPV(input_default_bindings=True, input_vo_keyboard=True)

        # 2. 【集成关键】观察核心属性 (Property Observation)
        # 这是 mpv API 的精髓。当 'time-pos' 属性变化时，自动调用 on_position_changed
        self._player.observe_property('time-pos', self.on_position_changed)
        self._player.observe_property('duration', self.on_duration_changed)
        # 'pause' 属性直接反映了播放/暂停状态
        self._player.observe_property('pause', self.on_pause_state_changed)

    def set_video_widget(self, widget):
        """将视频输出绑定到UI层的Widget上。mpv需要窗口ID(wid)。"""
        # 在 mpv 中，这个属性叫做 'wid' (Window ID)
        self._player.wid = widget.winId()

    def set_media(self, file_path: str):
        """加载并播放媒体文件。"""
        # mpv 的 play 命令会加载并自动开始播放
        self._player.play(file_path)
        # 确保初始状态是播放
        self._player.pause = False

    def play_pause(self):
        """切换播放/暂停状态，通过修改 'pause' 属性实现。"""
        self._player.pause = not self._player.pause

    def set_position(self, position_ms: int):
        """
        跳转到指定位置。
        注意：上层UI(QSlider)传递的是毫秒(int)，而mpv的'time-pos'属性是秒(float)。
        我们需要在这里进行单位转换。
        """
        position_sec = position_ms / 1000.0
        self._player.time_pos = position_sec

    # --- 属性观察回调函数 ---
    
    def on_position_changed(self, name, value):
        # value 是 mpv 传来的秒数 (float)，可能为 None
        if value is not None:
            # 转换为毫秒 (int) 后再发射信号，以匹配UI层的单位
            self.position_changed.emit(int(value * 1000))

    def on_duration_changed(self, name, value):
        # value 是 mpv 传来的总秒数 (float)，可能为 None
        if value is not None:
            self.duration_changed.emit(int(value * 1000))

    def on_pause_state_changed(self, name, is_paused):
        # is_paused 是 mpv 传来的布尔值
        if is_paused is not None:
            # is_playing 是 is_paused 的反义
            self.playback_state_changed.emit(not is_paused)

