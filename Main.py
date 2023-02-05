import sys
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QLabel, QPushButton, QBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
import SubWindow


class Interface:
    """
    主窗口
    """
    def __init__(self):
        self.app = QApplication(sys.argv)

        # 版本名称
        self.version = 'v0.9'

        # 主窗口初始化
        self.main_window_init()

        # 开始窗口初始化
        self.start_window_init()

        self.sub_windows = {}

        sys.exit(self.app.exec_())

    def main_window_init(self):
        """
        主窗口初始化
        :return:
        """
        main_window = QMainWindow()
        main_window.resize(800, 800)
        main_window.show()
        main_window.setWindowTitle('美女图片下载器' + self.version)
        main_window.setWindowIcon(QIcon('gpd.ico'))

        self.main_window = main_window

    def start_window_init(self):
        """
        开始窗口初始化
        :return:
        """
        # 开始窗口初始化
        start_window = QWidget(self.main_window)
        start_window.resize(self.main_window.width(), self.main_window.height())
        start_window.show()

        # 开始窗口布局
        start_window_layout = QBoxLayout(QBoxLayout.TopToBottom, start_window)

        # 开始窗口欢迎词
        tittle_label = QLabel(start_window)
        tittle_label.show()
        tittle_label.setText('欢迎使用')
        tittle_label.setAlignment(Qt.AlignCenter)
        tittle_label.setStyleSheet('font-size: 50px;color: black;')
        start_window_layout.addWidget(tittle_label)

        # 清新美女子窗口跳转按钮
        btn_fresh = QPushButton('清新美女', start_window)
        btn_fresh.show()
        btn_fresh.clicked.connect(lambda: self.switch_into_sub_window(SubWindow.WindowType.fresh))
        start_window_layout.addWidget(btn_fresh)

        # 清纯少女子窗口跳转按钮
        btn_pure = QPushButton('清纯少女', start_window)
        btn_pure.show()
        btn_pure.clicked.connect(lambda: self.switch_into_sub_window(SubWindow.WindowType.pure))
        start_window_layout.addWidget(btn_pure)

        # 摄影写真子窗口跳转按钮
        btn_photography = QPushButton('摄影写真', start_window)
        btn_photography.show()
        btn_photography.clicked.connect(lambda: self.switch_into_sub_window(SubWindow.WindowType.photography))
        start_window_layout.addWidget(btn_photography)

        # 青春风子窗口跳转按钮
        btn_youth = QPushButton('青春风', start_window)
        btn_youth.show()
        btn_youth.clicked.connect(lambda: self.switch_into_sub_window(SubWindow.WindowType.youth))
        start_window_layout.addWidget(btn_youth)

        # 退出按钮
        btn_exit = QPushButton('退出', start_window)
        btn_exit.show()
        btn_exit.clicked.connect(lambda: sys.exit())
        start_window_layout.addWidget(btn_exit)

        self.start_window = start_window

    def switch_into_sub_window(self, window_type: SubWindow.WindowType):
        sub_window = self.get_sub_window(window_type)
        sub_window.sub_window.show()
        self.start_window.hide()

    def get_sub_window(self, window_type: SubWindow.WindowType) -> SubWindow.SubWindow:
        """
        获取对应子窗口
        :param window_type:
        :return:
        """
        if window_type not in self.sub_windows:
            self.generate_sub_window(window_type)
        return self.sub_windows.get(window_type)

    def generate_sub_window(self, window_type: SubWindow.WindowType):
        """
        生成子窗口，并写入sub_windows
        :return:
        """
        sub_window = SubWindow.SubWindow(self.start_window, window_type)
        self.sub_windows.update({window_type: sub_window})


if __name__ == '__main__':
    main_interface = Interface()
