from PySide6.QtSvg import QSvgRenderer
from PySide6.QtGui import (QColor, QIcon, QPainter, QPixmap)
import os
from PySide6.QtCore import Qt, QSize
from iconmanager.theme import THEMES

class IconManager:
    """
    一个集中管理和着色应用程序图标的类。
    """
    def __init__(self, theme_name: str, base_path: str = 'icons'):
        """
        初始化图标管理器。
        :param theme: 主题名称。
        :param base_path: 存放SVG文件的基础路径。
        """
        # 如果传入的是带.xml后缀的文件名，先清理一下
        if theme_name.endswith('.xml'):
            theme_name = theme_name[:-4]

        color_key = 'secondaryTextColor'
            
        icon_color = THEMES[theme_name]['colors'][color_key]

        self.icon_color = QColor(icon_color)
        self.base_path = base_path
        self._icon_cache = {}  # 用于缓存已创建的图标

    def _create_colored_icon(self, svg_name: str) -> QIcon:
        """
        内部辅助函数，加载一个SVG文件并将其渲染为指定颜色的QIcon。
        （这就是我们之前写的那个函数，现在封装为类的一个私有方法）
        """
        # 如果图标已在缓存中，直接返回，无需重复创建
        if svg_name in self._icon_cache:
            return self._icon_cache[svg_name]

        svg_path = os.path.join(self.base_path, svg_name)
        
        renderer = QSvgRenderer(svg_path)
        pixmap = QPixmap(renderer.defaultSize())
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        renderer.render(painter)
        
        painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
        painter.fillRect(pixmap.rect(), self.icon_color)
        painter.end()
        
        icon = QIcon(pixmap)
        self._icon_cache[svg_name] = icon  # 将新创建的图标存入缓存
        return icon

    # --- 公共API方法 ---
    # 现在，您可以为您需要的每个图标创建一个简单的“getter”方法

    def get_add_icon(self) -> QIcon:
        return self._create_colored_icon('add.svg')

    def get_delete_icon(self) -> QIcon:
        return self._create_colored_icon('delete.svg')

    def get_edit_icon(self) -> QIcon:
        return self._create_colored_icon('edit.svg')

    def get_save_icon(self) -> QIcon:
        return self._create_colored_icon('save.svg')
    
    def get_file_open_icon(self) -> QIcon:
        return self._create_colored_icon('file_open.svg')
    
    def get_warning_icon(self) -> QIcon:
        return self._create_colored_icon('warning.svg')
    
    def get_play_icon(self) -> QIcon:
        return self._create_colored_icon('play.svg')
    
    def get_pause_icon(self) -> QIcon:
        return self._create_colored_icon('pause.svg')
    

    def get_volume_high_icon(self) -> QIcon:
        return self._create_colored_icon('volume_high.svg')
    
    def get_volume_off_icon(self) -> QIcon:
        return self._create_colored_icon('volume_off.svg')

    def get_app_icon(self) -> QIcon:
        """
        获取应用程序的图标。
        :return: QIcon对象
        """
        app_icon_path = os.path.join(self.base_path, 'app.ico')
        return QIcon(app_icon_path)