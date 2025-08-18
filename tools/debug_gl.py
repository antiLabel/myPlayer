# tools/debug_gl.py  —— 仅 PySide6
from dataclasses import dataclass
from typing import Optional

from PySide6.QtCore import QObject, Slot
from PySide6.QtGui import QOpenGLExtraFunctions
from PySide6.QtOpenGL import QOpenGLDebugLogger, QOpenGLDebugMessage

# 常量（避免引 PyOpenGL）
GL_FRAMEBUFFER = 0x8D40
GL_FRAMEBUFFER_BINDING = 0x8CA6
GL_FRAMEBUFFER_COMPLETE = 0x8CD5

_STATUS_NAME = {
    0x8CD5: "GL_FRAMEBUFFER_COMPLETE",
    0x8CD6: "GL_FRAMEBUFFER_INCOMPLETE_ATTACHMENT",
    0x8CD7: "GL_FRAMEBUFFER_INCOMPLETE_MISSING_ATTACHMENT",
    0x8CDB: "GL_FRAMEBUFFER_INCOMPLETE_DRAW_BUFFER",
    0x8CDC: "GL_FRAMEBUFFER_INCOMPLETE_READ_BUFFER",
    0x8CDD: "GL_FRAMEBUFFER_UNSUPPORTED",
    0x8CDF: "GL_FRAMEBUFFER_INCOMPLETE_MULTISAMPLE",
    0x8D56: "GL_FRAMEBUFFER_INCOMPLETE_LAYER_TARGETS",
}

@dataclass
class GLDiagHandles:
    logger: Optional[QOpenGLDebugLogger]
    funcs: QOpenGLExtraFunctions

class GLDiagnostics(QObject):
    """
    用法（在 QOpenGLWidget.initializeGL() 里）：
        self._diag = GLDiagnostics(self.context())
        self._diag.start()
        self._diag.check_fbo("after-init")
    然后在 paintGL() 前后各调一次 check_fbo()。
    """

    def __init__(self, gl_context):
        super().__init__()
        self._ctx = gl_context
        self._logger: Optional[QOpenGLDebugLogger] = None
        self._funcs = QOpenGLExtraFunctions(self._ctx)
        self._funcs.initializeOpenGLFunctions()

    def start(self) -> GLDiagHandles:
        # 需要 DebugContext 已启用；此时当前上下文就是 QOpenGLWidget 的 context()
        self._logger = QOpenGLDebugLogger(self._ctx)
        if not self._logger.initialize():
            print("[GLDiag] QOpenGLDebugLogger.initialize() 失败（可能未启用 DebugContext）")
            return GLDiagHandles(None, self._funcs)

        self._logger.messageLogged.connect(self._on_message)
        # 同步模式：哪条 gl* 语句触发，立即打印
        self._logger.startLogging(QOpenGLDebugLogger.LoggingMode.SynchronousLogging)
        print("[GLDiag] KHR_debug 已启动（同步模式）")
        return GLDiagHandles(self._logger, self._funcs)

    @Slot(QOpenGLDebugMessage)
    def _on_message(self, msg: QOpenGLDebugMessage):
        print(
            f"[KHR] id={msg.id()} src={msg.source().name} "
            f"type={msg.type().name} sev={msg.severity().name} :: {msg.message()}"
        )

    def check_fbo(self, tag: str = ""):
        f = self._funcs

        # 读取当前绑定 FBO
        try:
            from ctypes import c_int
            buf = (c_int * 1)()
            f.glGetIntegerv(GL_FRAMEBUFFER_BINDING, buf)
            bound = int(buf[0])
        except Exception:
            bound = -1

        # 完整性检查
        try:
            status = int(f.glCheckFramebufferStatus(GL_FRAMEBUFFER))
        except Exception as e:
            print(f"[GLDiag] glCheckFramebufferStatus 失败: {e!r}")
            return

        status_name = _STATUS_NAME.get(status, hex(status))
        prefix = f"[FBO] {tag} " if tag else "[FBO] "
        print(f"{prefix}bound={bound}, status={status_name}")
        if status != GL_FRAMEBUFFER_COMPLETE:
            print("[FBO] ⚠️ 不完整 —— 请核对附件/DrawBuffers/多重采样/层目标等。")
