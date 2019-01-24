#!/usr/bin/python
#-*-coding:utf-8 -*-
import _thread
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlencode, parse_qs, urlsplit, urlunsplit
from urllib.request import urlretrieve
import urllib.request
import os
import time
import threading


# 1024 http request header
# 1024 网站请求头
proxt_1024_req_header = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
    'Cache-Control': 'max-age=0',
    # 'Connection': 'keep - alive',
    'Cookie': '__cfduid=d4e99b476e7372dec9a44b67f533f37aa1548178386; aafaf_lastvisit=0%091548178386%' \
                  '09%2Fpw%2Fthread.php%3Ffid-5-page-5.html; aafaf_lastpos=F5; aafaf_threadlog=%2C5%2C; ' \
                  'aafaf_ol_offset=32368318; UM_distinctid=168769f77ac958-0509e825886dfc-46564b55-1fa400-16876' \
                  '9f77ad1302; CNZZDATA1261158850=393281613-1548174901-%7C1548174901',
    'Host': 'w3.jbzcjsj.pw',
    # 'Pragma': 'no-cache',
    'Proxy-Connection': 'keep-alive',
    'Referer': 'http://w3.jbzcjsj.pw/pw/thread-htm-fid-5-page-5.html',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)' \
                  ' Chrome/70.0.3538.102 Safari/537.36 OPR/57.0.3098.116'
}
request_header = proxt_1024_req_header

# magnet-link website http request header
# 磁力链接网站网站请求头
proxt_torrent_req_header = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
    'Cache-Control': 'no-cache',
    # 'Connection': 'keep - alive',
    'Cookie': '__cfduid=d7f5104b5a516916674841b656d67dde31548178497; UM_distinctid=16876a1266dfb2-018bb685bad' \
                  '0ed-46564b55-1fa400-16876a1266e1d2; CNZZDATA1273152310=501204684-1548176963-http%253A%2' \
                  '52F%252Fw3.jbzcjsj.pw%252F%7C1548176963; _ga=GA1.2.1886522142.1548178499; _gid=GA1.2.16499' \
                  '32666.1548178499; _gat=1',
    'Host': 'www1.downsx.com',
    'Pragma': 'no-cache',
    'Proxy-Connection': 'keep-alive',
    'Referer': 'http://w3.jbzcjsj.pw/pw/html_data/5/1901/3863561.html',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 ' \
              '(KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 OPR/57.0.3098.116'
}
torrent_request_header = proxt_torrent_req_header
opener=urllib.request.build_opener()
opener.addheaders=[('User-Agent','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36' \
                  ' (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 OPR/57.0.3098.116')]
urllib.request.install_opener(opener)

# proxy settings
# 代理设置
proxies = {'http': '127.0.0.1:1080', "https": "127.0.0.1:1080", }
proxies_header = proxies
isProxy = False                                                                  # 是否设置代理

base_url = "http://w3.jbzcjsj.pw/pw/"                                           # 基础url
save_path = "D:/code/Pycharm/1024Spider/torrent_asian_nomosaic"                  # 存储图片路径
fid = 5                                                                          # fid=5 表示亚洲无码
page_start = 1                                                                   # 爬取的开始页
page_end = 928                                                                   # 爬取的结束页
thread_num = 1                                                                   # 线程数


# conversion encode
# 转换编码
def Encode_Conversion(req):
    if req.encoding == 'ISO-8859-1':
        encodings = requests.utils.get_encodings_from_content(req.text)
        if encodings:
            encoding = encodings[0]
        else:
            encoding = req.apparent_encoding
        # encode_content = req.content.decode(encoding, 'replace').encode('utf-8', 'replace')
        encode_content = req.content.decode(encoding, 'replace')
        return encode_content
    else:
        return ""


# save [content] to [path]
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


# torrent and magnet-link page
# 种子/磁力链接页面
def Prase_Torrent(id, url, folder_path):
    try:
        if (isProxy == True):
            req = requests.get(url, params=torrent_request_header, proxies=proxies_header)
        else:
            req = requests.get(url, params=torrent_request_header)

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


# each post page
# 每个帖子页面
def Prase_Post(id, url, folder_name):
    try:
        if (isProxy == True):
            req = requests.get(url, params=request_header, proxies=proxies_header)
        else:
            req = requests.get(url, params=request_header)

        # 转换编码
        encode_content = Encode_Conversion(req)
        # soup转换
        soup = BeautifulSoup(encode_content, "html.parser")

        post_content = soup.select('div[id="read_tpc"]')
        post_content_num = len(post_content)
        if post_content_num == 0:
            print("[" + str(id) + "] No match post.")
            return

        # 创建保存的文件夹
        folder_path = save_path + '/' + folder_name
        folder = os.path.exists(folder_path)
        if not folder:
            os.makedirs(folder_path)
            print("[" + str(id) + "] Created folder " + folder_name)

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
                            urllib.request.urlretrieve(obj, folder_path + '/' + img_name)
                        except Exception as e:
                            print("[" + str(id) + "] Download the picture Exception: " + str(e))
                        else:
                            print("[" + str(id) + "] Successfully save the image to " + folder_path + '/' + img_name)
            else:
                # 匹配失败
                print("[" + str(id) + "] No match: " + str_content)
        # 保存到文件
        if magnet_link != '':
            result = result + '\n\n' + magnet_link
        Save_Text(id, folder_path + '/index.txt', result)
    except Exception as e:
        print("[" + str(id) + "] Prase_Post Exception: " + str(e))


# post list page
# 帖子列表页面
def Post_list(id, page):
    try:
        post_url = base_url + 'thread-htm-fid-' + str(fid) + '-page-' + str(page) + '.html'
        print('[' + str(id) + '] clicked: ' + post_url)

        if (isProxy == True):
            req = requests.get(post_url, params=request_header, proxies=proxies_header)
        else:
            req = requests.get(post_url, params=request_header)

        # 转换编码
        encode_content = Encode_Conversion(req)

        # soup转换
        soup = BeautifulSoup(encode_content, "html.parser")
        # 获取章节名称
        post_list = soup.select('tr[class="tr3 t_one"] h3 a')
        post_num = len(post_list)
        if post_num == 0:
            print("[" + str(id) + "] No match post_list.")
            return
        for post in post_list:
            str_post = str(post)
            # html网页的匹配
            matchObj = re.match(r'(.*)href="(.*)" id=(.*)>(.*?)</a>', str_post, re.M | re.I)
            if matchObj:
                post_url = matchObj.group(2)  # URL
                post_name = matchObj.group(4)  # 文件夹名
                if post_name != '':
                    # 匹配每个帖子
                    Prase_Post(id, base_url + post_url,
                               post_name.replace(u'\0', u'').replace(u'/', u'.').replace(u'?',
                                                                                         u'').replace(u'*',
                                                                                                      u''))
            else:
                # 匹配失败
                print("[" + str(id) + "] No match: " + str_post)
    except Exception as e:
        print("[" + str(id) + "] Post_list Exception." + str(e))


# multi-threaded, the parameter [id] is the thread id
# 多线程，参数 [id] 为线程 id
def Work_thread(id):
    try:
        if id <= page_end:
            prase_num = 0
            prase_more_one = 0
            page_num = abs(page_end - page_start) + 1
            if id <= int(page_num % thread_num):
                prase_more_one = 1
            page_num_each_thread = int(page_num / thread_num) + prase_more_one
            for each_page in range(page_start + id - 1, page_end + 1, thread_num):
                Post_list(id, each_page)
                prase_num += 1
                print('[' + str(id) + '] [ ' + "{:.1f}".format(
                    prase_num / page_num_each_thread * 100) + '% page completed ] ')
            print('[' + str(id) + '] completed !!!!!')
    except Exception as e:
        print("[" + str(id) + "] Work_thread Exception." + str(e))


if __name__ == "__main__":
    # single thread # 单线程
    # Work_thread(1)
    # multithreading # 多线程
    try:
        for i in range(1, thread_num + 1):
            _thread.start_new_thread(Work_thread, (i,))
    except Exception as e:
        print("Start_new_thread Exception: " + str(e))
    while 1:
        pass
