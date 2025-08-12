# media_player.py - 模型/服务层 (Model/Service)
# 职责：封装所有与QMediaPlayer相关的核心功能，并对外提供简单的接口和信号。

from PySide6.QtCore import QObject, Signal, QUrl
from PySide6.QtMultimedia import QMediaPlayer
from PySide6.QtMultimediaWidgets import QVideoWidget

class MediaPlayerService(QObject):
    """
    这个类是播放器的“引擎”。它不关心UI长什么样，只负责播放、暂停、跳转等媒体核心任务。
    它通过Qt的信号机制将内部状态的变化(如播放位置、播放状态)通知给外部。
    """
    # 定义信号，用于通知Controller/View层状态已改变
    position_changed = Signal(int)
    duration_changed = Signal(int)
    playback_state_changed = Signal(QMediaPlayer.PlaybackState)

    # 为了方便，我们直接引用QMediaPlayer的枚举状态
    PlayingState = QMediaPlayer.PlayingState
    PausedState = QMediaPlayer.PausedState
    StoppedState = QMediaPlayer.StoppedState

    def __init__(self, parent=None):
        super().__init__(parent)
        self._player = QMediaPlayer()
        self._video_widget = QVideoWidget()
        self._player.setVideoOutput(self._video_widget)

        # 连接QMediaPlayer的内部信号到我们自己的信号上
        self._player.positionChanged.connect(self.position_changed)
        self._player.durationChanged.connect(self.duration_changed)
        self._player.playbackStateChanged.connect(self.playback_state_changed)

    def get_video_widget(self):
        """返回视频显示的Widget，以便UI层可以将其嵌入到布局中"""
        return self._video_widget

    def set_media(self, url: QUrl):
        """设置要播放的媒体文件"""
        self._player.setSource(url)

    def play_pause(self):
        """切换播放/暂停状态"""
        if self._player.playbackState() == self.PlayingState:
            self._player.pause()
        else:
            self._player.play()

    def set_position(self, position: int):
        """跳转到指定位置"""
        self._player.setPosition(position)
