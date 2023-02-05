import requests
from PyQt5.QtWidgets import QWidget, QMainWindow, QLabel, QPushButton, QBoxLayout, QComboBox
from PyQt5.QtCore import Qt, QThread
from PyQt5.QtGui import QImage, QPixmap
from enum import Enum
import random

import PictureRequest


class WindowType(Enum):
    """
    子窗口名称和地址
    """
    fresh = '清新美女', "https://www.vmgirls.net/fresh/page/"
    pure = '清纯少女', "https://www.vmgirls.net/pure/page/"
    photography = '摄影写真', "https://www.vmgirls.net/photography/page/"
    youth = '青春风', "https://www.vmgirls.net/youth/page/"

    def get_type_name(self):
        """
        获取类型中文名
        :return:
        """
        return self.value[0]

    def get_url(self):
        """
        获取类型对应的url
        :return:
        """
        return self.value[1]


class SubWindow:
    # 子窗口类 用做展示界面
    def __init__(self, start_window: QWidget, window_type: WindowType):
        self.main_window: QMainWindow = start_window.parent()
        self.start_window = start_window
        self.window_type = window_type

        # 创建爬虫类
        self.request = PictureRequest.Request(window_type.get_url())

        # 初始化该窗口
        self.sub_window_init()

        # 下载全部图片进程
        self.download_threads: list[QThread] = []

    def sub_window_init(self):
        """
        子窗口初始化
        :return:
        """
        sub_window = QWidget(self.main_window)
        sub_window.resize(self.main_window.width(), self.main_window.height())
        sub_window.show()

        self.sub_window = sub_window

        # 建立垂直布局
        sub_window_layout = QBoxLayout(QBoxLayout.TopToBottom, sub_window)

        index_tittle_label = QLabel(sub_window)
        index_tittle_label.show()
        index_tittle_label.setText(self.window_type.get_type_name())
        index_tittle_label.setAlignment(Qt.AlignCenter)
        index_tittle_label.setStyleSheet('font-size:30px;color: red;')

        sub_window_layout.addWidget(index_tittle_label)

        # 图片链接展示布局，整体为横向布局，链接展示为纵向
        picture_main_layout = QBoxLayout(QBoxLayout.LeftToRight)
        sub_window_layout.addLayout(picture_main_layout)

        picture_left_layout = QBoxLayout(QBoxLayout.TopToBottom)
        picture_right_layout = QBoxLayout(QBoxLayout.TopToBottom)

        picture_main_layout.addLayout(picture_left_layout)
        picture_main_layout.addLayout(picture_right_layout)


        # 图片分左右展示
        html_dict = self.request.get_current_page()
        half_picture_num = int(len(html_dict) / 2)
        left_html_dict = dict(list(html_dict.items())[:half_picture_num])
        right_html_dict = dict(list(html_dict.items())[half_picture_num:])

        # 左半部分
        for dic in left_html_dict.items():
            dict_item = list(dic)
            picture_left_layout.addWidget(self.generate_picture_label(dict_item))

        # 右半部分
        for dic in right_html_dict.items():
            dict_item = list(dic)
            picture_right_layout.addWidget(self.generate_picture_label(dict_item))


        # 跳转页面布局
        switch_page_layout = QBoxLayout(QBoxLayout.LeftToRight, sub_window)

        # 返回按钮
        back_button = QPushButton(self.sub_window)
        back_button.show()
        back_button.setText('返回主页')
        back_button.clicked.connect(lambda: (sub_window.hide(), self.start_window.show()))
        switch_page_layout.addWidget(back_button)

        # 上一页
        pre_page_btn = QPushButton(self.sub_window)
        pre_page_btn.show()
        pre_page_btn.setText('上一页')
        pre_page_btn.clicked.connect(lambda: self.sub_window_switch_page(self.request.curr_page-1))
        switch_page_layout.addWidget(pre_page_btn)

        # 展示当前页数
        page_label = QLabel(self.sub_window)
        page_label.show()
        page_label.setText(f'当前{self.request.curr_page}页，一共{self.request.max_page}页')
        page_label.setAlignment(Qt.AlignCenter)
        switch_page_layout.addWidget(page_label)

        # 下一页
        post_page_btn = QPushButton(self.sub_window)
        post_page_btn.show()
        post_page_btn.setText('下一页')
        post_page_btn.clicked.connect(lambda: self.sub_window_switch_page(self.request.curr_page+1))
        switch_page_layout.addWidget(post_page_btn)

        # 跳转页
        jump_page_combox = QComboBox(self.sub_window)
        jump_page_combox.show()
        jump_page_combox.addItems([x.__str__() for x in range(self.request.min_page, self.request.max_page + 1)])
        jump_page_combox.setCurrentIndex(self.request.curr_page - 1)
        switch_page_layout.addWidget(jump_page_combox)

        # 跳转页按钮
        jump_page_btn = QPushButton('跳转', self.sub_window)
        jump_page_btn.show()
        jump_page_btn.clicked.connect(lambda: self.sub_window_switch_page(jump_page_combox.currentIndex() + 1))
        switch_page_layout.addWidget(jump_page_btn)

        def download_all_pictures(window: SubWindow):
            """
            下载当前页面全部图片
            :return:
            """
            class DownLoadThread(QThread):
                def __init__(self, window: SubWindow):
                    super(DownLoadThread, self).__init__()
                    self.window = window

                def run(self) -> None:
                    for it in html_dict.items():
                        itl = list(it)
                        self.window.request.download_tittle_pictures(itl[0], itl[1][0])
            download_thread = DownLoadThread(window)
            self.download_threads.append(download_thread)
            download_thread.start()

            # 刷新线程池
            for thread in self.download_threads:
                if thread.isFinished():
                    self.download_threads.remove(thread)

        # 下载当前页全部图片
        download_all_btn = QPushButton(self.sub_window)
        download_all_btn.show()
        download_all_btn.setText('下载全部')
        download_all_btn.clicked.connect(lambda: download_all_pictures(self))
        switch_page_layout.addWidget(download_all_btn)

        sub_window_layout.addLayout(switch_page_layout)

    def generate_picture_label(self, title_html_picture_item: list):
        def show_picture():
            img_url = title_html_picture_item[1][1]
            if img_url != '':
                res = requests.get(img_url)
                img = QImage.fromData(res.content)
                img_label = QLabel()
                img_label.setPixmap(QPixmap.fromImage(img))
                img_label.setWindowTitle(title_html_picture_item[0])
                img_label.show()
                show_list.append(img_label)
            else:
                img_label = QLabel('暂无图片')
                img_label.show()
                show_list.append(img_label)

        image_window = QWidget(self.sub_window)
        image_window.show()

        # 主布局
        image_main_layout = QBoxLayout(QBoxLayout.LeftToRight, image_window)

        # 图片标题
        tittle_label = QLabel(image_window)
        tittle_label.show()
        tittle_label.setText(title_html_picture_item[0])
        tittle_label.setStyleSheet(
            f'color: rgb({random.randint(0, 255)},{random.randint(0, 255)},{random.randint(0, 255)});')
        image_main_layout.addWidget(tittle_label)

        show_list = []
        show_button = QPushButton(image_window)
        show_button.show()
        show_button.setText('展示封面图')
        show_button.clicked.connect(lambda: show_picture())
        image_main_layout.addWidget(show_button)

        download_button = QPushButton(image_window)
        download_button.show()
        download_button.setText('下载套图')
        download_button.clicked.connect(
            lambda: self.request.download_tittle_pictures(title_html_picture_item[0], title_html_picture_item[1][0]))
        image_main_layout.addWidget(download_button)

        return image_window

    def sub_window_switch_page(self, target_page_number: int):
        if self.request.is_able_switch_page(target_page_number):
            self.request.switch_page(target_page_number)
            self.sub_window.hide()
            self.sub_window.destroy()
            self.sub_window = QWidget(self.main_window)
            self.sub_window_init()
