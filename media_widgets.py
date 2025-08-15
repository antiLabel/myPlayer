# media_widgets.py (已重构)

from PySide6.QtWidgets import QWidget, QPushButton, QSlider, QHBoxLayout, QVBoxLayout, QLabel
from PySide6.QtCore import Qt, QTimer, QEvent

class PlayerUI(QWidget):
    def __init__(self, icon_manager, parent=None):
        super().__init__(parent)
        self.icon_manager = icon_manager
        # 允许捕获鼠标移动事件，即使没有按下按钮
        self.setMouseTracking(True)

        # --- 创建控件 ---
        # 视频层是基础

        # 控制层是悬浮的
        self.control_widget = QWidget(self)
        self.control_widget.setStyleSheet("background-color: rgba(0, 0, 0, 150);")
        self.video_frame = QWidget(self)
        self.control_widget.setAttribute(Qt.WA_NativeWindow, True)

        self.current_time_label = QLabel("00:00")
        self.total_time_label = QLabel("00:00")
        self.play_button = QPushButton()
        self.slider = QSlider(Qt.Horizontal)
        self.mute_button = QPushButton()
        self.volume_slider = QSlider(Qt.Horizontal)

        self._setup_widgets_properties()
        self._setup_control_layout()

        # --- 事件处理与定时器 ---
        self.volume_hide_timer = QTimer(self)
        self.volume_hide_timer.setInterval(2000)  # 2秒延时
        self.volume_hide_timer.setSingleShot(True)
        self.volume_hide_timer.timeout.connect(self.volume_slider.hide)

        # 安装事件过滤器，以捕获静音按钮和音量条上的鼠标事件
        self.mute_button.installEventFilter(self)
        self.volume_slider.installEventFilter(self)

        # 初始状态下，隐藏所有控件
        self.control_widget.hide()
        self.volume_slider.hide()

    def _setup_widgets_properties(self):
        """配置控件的属性"""
        self.play_button.setIcon(self.icon_manager.get_play_icon())
        self.play_button.setStatusTip("播放/暂停")
        self.play_button.setFlat(True)
        self.play_button.setEnabled(False)

        self.slider.setRange(0, 0)

        self.mute_button.setIcon(self.icon_manager.get_volume_up_icon())
        self.mute_button.setFlat(True)
        self.mute_button.setEnabled(False)

        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(100)
        self.volume_slider.setFixedWidth(100)
        self.volume_slider.setEnabled(False)

    def _setup_control_layout(self):
        
        layout = QHBoxLayout(self.control_widget)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.addWidget(self.play_button)
        layout.addWidget(self.current_time_label)
        layout.addWidget(self.slider)
        layout.addWidget(self.total_time_label)
        layout.addStretch()
        layout.addWidget(self.volume_slider)
        layout.addWidget(self.mute_button)

    # --- 事件重写，用于实现悬浮效果 ---

    def resizeEvent(self, event):
        """当窗口大小改变时，手动重新定位视频层和控制层"""
        super().resizeEvent(event)
        # 视频层始终填满整个控件
        self.video_frame.setGeometry(self.rect())
        # 控制层位于底部，并留出一些边距
        control_height = self.control_widget.sizeHint().height()
        margin = 0
        self.control_widget.setGeometry(
            margin, 
            self.height() - control_height - margin, 
            self.width() - 2 * margin, 
            control_height
        )

    def enterEvent(self, event):
        """鼠标进入播放器区域时，显示控制栏"""
        super().enterEvent(event)
        self.control_widget.show()

    def leaveEvent(self, event):
        """鼠标离开播放器区域时，隐藏控制栏"""
        super().leaveEvent(event)
        self.control_widget.hide()

    def eventFilter(self, watched, event):
        """
        事件过滤器，用于处理静音按钮和音量条的特殊交互
        """
        if watched is self.mute_button or watched is self.volume_slider:
            if event.type() == QEvent.Type.Enter:
                # 鼠标进入任一控件，都停止计时器并显示音量条
                self.volume_hide_timer.stop()
                self.volume_slider.show()
                return True  # 事件已处理
            elif event.type() == QEvent.Type.Leave:
                # 鼠标离开任一控件，都启动延时隐藏的计时器
                self.volume_hide_timer.start()
                return True  # 事件已处理

        return super().eventFilter(watched, event)

    # --- 用于更新UI的公共槽函数 ---

    def _format_time(self, ms: int) -> str:
        seconds = ms // 1000
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes:02d}:{seconds:02d}"

    def set_slider_range(self, duration_ms: int):
        self.slider.setRange(0, duration_ms)
        self.total_time_label.setText(self._format_time(duration_ms))
        self.play_button.setEnabled(True)
        self.mute_button.setEnabled(True)
        self.volume_slider.setEnabled(True)

    def update_slider_position(self, position_ms: int):
        if not self.slider.isSliderDown():
            self.slider.setValue(position_ms)
        self.current_time_label.setText(self._format_time(position_ms))

    def update_play_button_icon(self, is_playing: bool):
        if is_playing:
            self.play_button.setIcon(self.icon_manager.get_pause_icon())
        else:
            self.play_button.setIcon(self.icon_manager.get_play_icon())

    def update_volume_slider(self, volume: int):
        if not self.volume_slider.isSliderDown():
            self.volume_slider.setValue(volume)
            
    def update_mute_button_icon(self, is_muted: bool):
        if is_muted:
            self.mute_button.setIcon(self.icon_manager.get_volume_off_icon())
        else:
            self.mute_button.setIcon(self.icon_manager.get_volume_up_icon())