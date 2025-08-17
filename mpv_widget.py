from mpv import MpvRenderContext, MpvGlGetProcAddressFn
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtGui import QOpenGLContext
from PySide6.QtOpenGL import QOpenGLVersionProfile, QOpenGLDebugLogger, QOpenGLDebugMessage

class MPVWidget(QOpenGLWidget):
    def __init__(self, player_service, parent=None):
        self._gl_logger = None
        
        super().__init__(parent)
        self.player = player_service.get_player_handle()
        self.ctx = None

    def initializeGL(self):
        # get_proc 的签名必须是 (ctx, name)；name 为 bytes
        def _get_proc(_ctx, name):
            glctx = QOpenGLContext.currentContext()
            address = int(glctx.getProcAddress(name.decode('utf-8'))) if glctx else 0
            # 打印返回值，验证其是否为有效的非零整数
            print(f"  -> Returning address: {address}")
            
            # 断言检查
            assert isinstance(name, bytes), "错误：_get_proc 的 name 参数不是 bytes 类型！"
            if b'gl' in name: # 真正的OpenGL函数地址不应该是0
                assert address != 0, f"错误：未能找到函数 {name.decode('utf-8')} 的地址！"

            return address

        self.ctx = MpvRenderContext(
            self.player, 'opengl',
            opengl_init_params={'get_proc_address': MpvGlGetProcAddressFn(_get_proc)}
        )
        # 回调挂在渲染上下文
        self.ctx.update_cb = self.update
        self._start_gl_debug_logger()

    def paintGL(self):
        if not self.ctx:
            return
        dpr = self.devicePixelRatioF()  # Qt6 推荐
        w, h = int(self.width()*dpr), int(self.height()*dpr)
        fbo = int(self.defaultFramebufferObject())
        # 打印这些数值，以便观察
        print(f"paintGL: fbo={fbo}, width={w}, height={h}, dpr={dpr}")
        
        # 断言（Assert）是一种更严格的检查，如果条件不满足，程序会直接报错退出
        # 在窗口可见时，这些值应该是正数
        if self.isVisible():
            assert fbo > 0, "错误：Framebuffer ID (fbo) 无效！"
            assert w > 0 and h > 0, "错误：画布尺寸 (width/height) 无效！"
        # --- 结束调试代码 ---
        self.ctx.render(opengl_fbo={'fbo': fbo, 'w': w, 'h': h}, flip_y=True)

    def closeEvent(self, e):
        if self.ctx:
            self.ctx.free()
            self.ctx = None
        super().closeEvent(e)

    def disable_updates(self):
            """
            取消 update_cb 回调，以防止在播放结束后出现警告。
            """
            if self.ctx:
                print("MPVWidget: Disabling update callback.")
                self.ctx.update_cb = None


    def _start_gl_debug_logger(self):
            ctx = QOpenGLContext.currentContext()
            if not ctx:
                return  # 理论上不会发生；保险起见

            # 检查是否支持 KHR_debug（大多数桌面驱动都支持）
            if not ctx.hasExtension(b"GL_KHR_debug"):
                print("[GLDBG] GL_KHR_debug not supported; no driver-side messages.")
                return

            logger = QOpenGLDebugLogger(self)
            if not logger.initialize():
                print("[GLDBG] QOpenGLDebugLogger initialize() failed.")
                return

            def on_msg(msg: QOpenGLDebugMessage):
                # 常用字段：来源、类型、严重级别、ID、文本
                print(
                    "[GLDBG]",
                    f"src={msg.source()}, type={msg.type()}, sev={msg.severity()}, id={msg.id()}",
                    msg.message()
                )

            logger.messageLogged.connect(on_msg)

            # 同步模式：每条消息立即回调，便于和你的日志/断言对上时序
            logger.startLogging(QOpenGLDebugLogger.SynchronousLogging)

            self._gl_logger = logger
            print("[GLDBG] OpenGL debug logger started.")