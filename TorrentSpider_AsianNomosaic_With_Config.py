#!/usr/bin/python3
#-*-coding:utf-8 -*-
import _thread
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlencode, parse_qs, urlsplit, urlunsplit
from urllib.request import urlretrieve
import urllib.request
import os
import json


config = object


class JsonCommand(object):
    def __init__(self):
        try:
            with open('config.json', encoding='utf-8') as config_file:
                _config = json.loads(config_file.read())
            self.request_header = _config["_1024_req_header"]
            self.torrent_request_header = _config["_torrent_req_header"]
            self.proxies = _config["proxies"]
            self.is_proxy = bool(_config["is_proxy"])
            self.fid = int(_config["fid"])
            self.base_url = _config["base_url"]
            self.save_path = _config["save_path"]
            self.page_start = int(_config["page_start"])
            self.page_end = int(_config["page_end"])
            self.thread_num = int(_config["thread_num"])
            self.page_num = abs(self.page_end - self.page_start) + 1
            self.page_num_each_thread = self.page_num / self.thread_num
            self.user_agent = _config["_1024_req_header"]["User-Agent"]
            config_file.close()
        except Exception as e:
            print("JsonCommand Exception: " + str(e))


# 转换编码
def Encode_Conversion(req):
    if req.encoding == 'ISO-8859-1':
        encodings = requests.utils.get_encodings_from_content(req.text)
        if encodings:
            encoding = encodings[0]
        else:
            encoding = req.apparent_encoding

        # encode_content = req.content.decode(encoding, 'replace').encode('utf-8', 'replace')
        encode_content = req.content.decode(encoding, 'replace')  # 如果设置为replace，则会用?取代非法字符；
        return encode_content
    else:
        return ""


# 保存文本
def Save_Text(id, path, content):
    try:
        f = open(path, "w", encoding='utf-8')
        f.write(content)
    except IOError:
        print("[" + str(id) + "] IOError: File open failed.")
    except Exception as e:
        print("Save_Text Exception: " + str(e))
    else:
        # 内容写入文件成功
        print("[" + str(id) + "] Successfully save the file to " + path)
        f.close()


# 种子/磁力链接页面
def Prase_Torrent(id, url, folder_path):
    try:
        if (config.is_proxy == True):
            req = requests.get(url, params=config.torrent_request_header, proxies=config.proxies)
        else:
            req = requests.get(url, params=config.torrent_request_header)

        # soup转换
        soup = BeautifulSoup(req.content, "html.parser")

        torrent_content = soup.select('.uk-button ')
        torrent_content_num = len(torrent_content)
        if torrent_content_num == 0:
            print("[" + str(id) + "] No match torrent.")
            return ''
        for content in torrent_content:
            str_content = str(content)
            # 匹配磁力链接
            matchObj = re.search(r'magnet(.*?)"', str_content)
            if matchObj:
                magnet_link = 'magnet' + matchObj.group(1)
                return magnet_link
            else:
                # 匹配失败
                print("[" + str(id) + "] No match: " + str_content)
                return ''
    except Exception as e:
        print("[" + str(id) + "] Prase_Torrent Exception: " + str(e))


# 每个帖子页面
def Prase_Post(id, url, folder_name):
    try:
        folder_path = config.save_path + '/' + folder_name
        folder = os.path.exists(folder_path)
        if not folder:
            os.makedirs(folder_path)
            print("[" + str(id) + "] Created folder " + folder_name)

        if (config.is_proxy == True):
            req = requests.get(url, params=config.request_header, proxies=config.proxies)
        else:
            req = requests.get(url, params=config.request_header)

        # 转换编码
        encode_content = Encode_Conversion(req)
        # soup转换
        soup = BeautifulSoup(encode_content, "html.parser")

        post_content = soup.select('div[id="read_tpc"]')
        post_content_num = len(post_content)
        if post_content_num == 0:
            print("[" + str(id) + "] No match post.")
            return -1
        # 保存文本内容
        result = post_content[0].text
        magnet_link = ''
        for content in post_content:
            str_content = str(content)

            # 匹配种子
            matchObj = re.findall(r'href="(.*?)"', str_content)
            if matchObj:
                for obj in matchObj:
                    magnet_link = Prase_Torrent(id, obj, folder_path)
            else:
                # 匹配失败
                print("[" + str(id) + "] No match: " + str_content)

            # 匹配图片
            matchObj = re.findall(r'window.open\(\'(.*?)\'\);', str_content)
            if matchObj:
                for obj in matchObj:
                    objTemp = obj
                    strlist = objTemp.split('/')
                    strlen = len(strlist)
                    if strlen != 0:
                        img_name = strlist[strlen - 1]
                        try:
                            img_path = folder_path + '/' + img_name
                            urllib.request.urlretrieve(url=obj, filename=img_path)
                        except Exception as e:
                            print("[" + str(id) + "] Download the picture Exception: " + str(e))
                        else:
                            print("[" + str(id) + "] Successfully save the picture to " + folder_path + '/' + img_name)
            else:
                # 匹配失败
                print("[" + str(id) + "] No match: " + str_content)
        # 保存到文件
        if magnet_link != '':
            result = result + '\n\n' + magnet_link
        Save_Text(id, folder_path + '/index.txt', result)
    except Exception as e:
        print("[" + str(id) + "] Prase_Post Exception: " + str(e))


# 亚洲无码帖子列表页面
def Post_list(id, page):
    try:
        post_url = config.base_url + 'thread-htm-fid-' + str(config.fid) + '-page-' + str(page) + '.html'
        print('[' + str(id) + '] clicked: ' + post_url)

        if (config.is_proxy == True):
            req = requests.get(post_url, params=config.request_header, proxies=config.proxies)
        else:
            req = requests.get(post_url, params=config.request_header)

        # 转换编码
        encode_content = Encode_Conversion(req)

        # soup转换
        soup = BeautifulSoup(encode_content, "html.parser")
        # 获取章节名称
        post_list = soup.select('tr[class="tr3 t_one"] h3 a')
        post_num = len(post_list)
        if post_num == 0:
            print("[" + str(id) + "] No match post_list.")
            return -1
        for post in post_list:
            str_post = str(post)
            # html网页的匹配
            matchObj = re.match(r'(.*)href="(.*)" id=(.*)>(.*?)</a>', str_post, re.M | re.I)
            if matchObj:
                post_url = matchObj.group(2)  # URL
                post_name = matchObj.group(4)  # 文件夹名
                if post_name != '':
                    # 匹配每个帖子
                    if Prase_Post(id, config.base_url + post_url,
                                  post_name.replace(u'\0', u'').replace(u'/', u'.').replace(u'?',
                                                                                            u'').replace(u'*',
                                                                                                         u'')) == -1:
                        return -1
            else:
                # 匹配失败
                print("[" + str(id) + "] No match: " + str_post)
    except Exception as e:
        print("[" + str(id) + "] Post_list Exception." + str(e))


# 多线程下载
def Work_thread(id):
    try:
        if id <= config.page_end:
            for each_page in range(id, config.page_end, config.thread_num):
                Post_list(id, each_page)
                prase_num = each_page / config.thread_num
                print('[' + str(id) + '] [ ' + "{:.1f}".format(prase_num / config.page_num_each_thread * 100) + '% page completed ] ')
    except Exception as e:
        print("[" + str(id) + "] Work_thread Exception." + str(e))


if __name__ == "__main__":
    config = JsonCommand()
    opener = urllib.request.build_opener()
    opener.addheaders = [(config.user_agent)]
    urllib.request.install_opener(opener)
    # 单线程
    # Work_thread(1)
    # 多线程
    try:
        for i in range(1, config.thread_num + 1):
            _thread.start_new_thread(Work_thread, (i,))
    except Exception as e:
        print("Start_new_thread Exception: " + str(e))
    while 1:
        pass
