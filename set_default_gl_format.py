# ---- set_default_gl_format.py（或者直接写在 main.py 顶部）----
from PySide6.QtGui import QSurfaceFormat
from PySide6.QtWidgets import QApplication

def enable_debug_gl_default_format():
    fmt = QSurfaceFormat()
    fmt.setVersion(3, 3)                         # 你也可以按需 4.x
    fmt.setProfile(QSurfaceFormat.CoreProfile)   # 建议 Core Profile
    fmt.setSwapBehavior(QSurfaceFormat.DoubleBuffer)
    fmt.setOption(QSurfaceFormat.DebugContext, on=True)  # 开启调试上下文
    QSurfaceFormat.setDefaultFormat(fmt)
