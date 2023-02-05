import re
import os
import requests
from bs4 import BeautifulSoup



class Request:

    def __init__(self, url: str):
        # 原始url
        self.index_page = url
        # 默认从第一页开始
        self.curr_page = 1

        # 读取页数范围
        self.min_page = 1
        self.max_page = self.get_max_page()

        # 页面内容缓存
        self.page_cache: {int: dict} = {}

        # 下载进程
        self.download_threads = []

    def get_curr_url(self):
        """
        获取当前页的url
        :return:
        """
        return self.index_page + str(self.curr_page)

    def switch_page(self, target_page_number):
        """
        跳转页面
        :param target_page_number:
        :return:
        """
        if self.min_page <= target_page_number <= self.max_page:
            self.curr_page = target_page_number

    def is_able_switch_page(self, target_page_number):
        """
        判断是否可以跳转到目标页
        :param target_page_number:
        :return:
        """
        if self.min_page <= target_page_number <= self.max_page:
            return True
        return False

    @staticmethod
    def get_response(target_url: str):
        """

        :param target_url: 指定url
        :return: 返回url的response
        """
        headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36 "}
        response = requests.get(target_url, headers=headers)
        return response

    def get_max_page(self):
        # 获取最大页数
        response = self.get_response(self.get_curr_url())
        bs = BeautifulSoup(response.text)
        max_page_number = max(int(x[0]) for x in [re.findall(r'href="https://.*?page/(\d+)"', x.__str__()) for x in
                                                  bs.find_all('a', attrs={'class': 'page-numbers'})])
        return max_page_number


    def get_current_page(self) -> dict:
        """
            获取当前页的全部标题、跳转的url和对应展示图片的url，dict结构 标题: [地址，图片]
        """
        # 若页面缓存中已存在该页信息，则直接取出
        if self.curr_page in self.page_cache:
            return self.page_cache.get(self.curr_page)

        response = self.get_response(self.get_curr_url())
        bs = BeautifulSoup(response.text)
        picture_html_items = [
            re.findall(r'href="(.*?)"\sstyle="background-image: url\(\'(.*?)\'\)"\stitle="(.*?)"', x.__str__()) for x in
            bs.find_all('a', attrs={"class": "media-content"})]
        # dict结构 标题: [地址，图片]
        title_html_picture_dict = dict(
            zip([x[0][2] for x in picture_html_items], [[x[0][0], x[0][1]] for x in picture_html_items]))

        # 写入缓存
        self.page_cache.update({self.curr_page: title_html_picture_dict})

        return title_html_picture_dict

    def get_picture_urls(self, picture_html_url: str):
        """

        :param picture_html_url: 标题对应的页面url
        :return: 标题对应页面中的图片urls
        """
        response = self.get_response(picture_html_url)
        bs = BeautifulSoup(response.text)
        picture_urls = re.findall(r'src="(.*?)"',
                                  bs.find_all('div', attrs={"class": re.compile(r"post-content.*")}).__str__())
        return picture_urls

    def download_tittle_pictures(self, picture_tittle: str, picture_html_url: str):
        """
        入参图片标题和图片网站的url
        :param picture_tittle: 子页面标题
        :param picture_html_url: 子页面url
        :return:
        """

        # 创建对应目录
        if not os.path.exists('pictures'):
            os.mkdir('pictures')

        # 创建图片集目录
        if not os.path.exists(f'pictures/{picture_tittle}'):
            os.mkdir(f'pictures/{picture_tittle}')
        target_path = f'pictures/{picture_tittle}'

        # 获取该页面中对应的图片urls
        picture_urls = self.get_picture_urls(picture_html_url)
        for picture_url in picture_urls:
            picture_name = picture_url.split('/')[-1]
            self.download_pictures(picture_url, picture_name, target_path)

    def download_pictures(self, picture_url: str, picture_name: str, target_path: str):
        """
        :param picture_url: 图片url
        :param target_path: 下载的本地地址
        :param picture_name: 图片名称
        :return:
        """
        response = Request.get_response(picture_url)
        picture_path = f'{target_path}/{picture_name}'
        with open(picture_path, 'wb') as f:
            print(f'{picture_path}开始下载')
            f.write(response.content)
            print(f'{picture_path}已下载完成')
