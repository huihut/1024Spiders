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
import time
import pymysql

# 1024 http request header
# 1024 网站请求头
proxt_1024_req_header = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
    'Cache-Control': 'no-cache',
    # 'Connection': 'keep - alive',
    'Cookie': '__cfduid=d7e5c699ef4d6599ef01239424b0e6cd71547705542; aafaf_lastvisit=0%09154' \
              '7705542%09%2Fpw%2Findex.php%3F; UM_distinctid=1685a707030539-0653970bbabd2b-46564b55' \
              '-1fa400-1685a707031a0a; CNZZDATA1261158850=317005769-1547705297-%7C1547705297',
    'Host': 'w3.jbzcjsj.pw',
    'Pragma': 'no-cache',
    'Proxy-Connection': 'keep-alive',
    #'Referer': 'http://w3.afulyu.pw/pw/thread.php?fid=17&page=1',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 ' \
                  '(KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 OPR/57.0.3098.116'
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
    'Cookie': '__cfduid=d062c450fc125c2a02de05db8586dc1941547731587; UM_distinctid=1685bfdd4' \
              'd4854-0edeecf536f3fc-46564b55-1fa400-1685bfdd4d515b4; CNZZDATA1273152310=651528679' \
              '-1547731013-http%253A%252F%252Fw3.jbzcjsj.pw%252F%7C1547731013; _ga=GA1.2.845482462.' \
              '1547731588; _gid=GA1.2.2026642011.1547731588',
    'Host': 'www1.downsx.club',
    'Pragma': 'no-cache',
    'Proxy-Connection': 'keep-alive',
    'Referer': 'http://w3.jbzcjsj.pw/pw/html_data/3/1901/3855151.html',
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
isProxy = False                                         # whether to set proxy  # 是否设置代理

base_url = "http://w3.jbzcjsj.pw/pw/"                   # xp1024's base url     # xp1024的基本链接
save_path = "D:/code/Pycharm/1024Spider/torrent_asian_nomosaic"    # pictures save path # 图片保存路径
fid = 5                                                 # Fid=5 means Asian porn without mosaics. # Fid=5 表示亚洲无码
page_start = 1                                          # crawl start page      # 爬取的开始页
page_end = 913                                          # crawl end page        # 爬取的结束页
thread_num = 1                                          # number of threads     # 线程数
mySQLCommand = object


# Used to execute database commands
# 用于执行数据库命令
class MySQLCommand(object):
    # init # 类的初始化
    def __init__(self):
        self.host = ''                                  # host ip or domain name，local is [127.0.0.1] # 数据库所在的主机
        self.port = 3306                                # database port             # 数据库端口号
        self.user = ''                                  # database username         # 数据库用户名
        self.password = ""                              # database password         # 数据库密码
        self.db = ""                                    # database name             # 数据库名
        self.table_torrent = "AsianNomosaic"            # porn information table    # 影片信息表
        self.table_pictures = "AsianNomosaicPictures"   # pictures table            # 图片表

    # connect to database
    # 连接数据库
    def connect_mysql(self):
        try:
            self.conn = pymysql.connect(host=self.host, port=self.port, user=self.user,
                                        passwd=self.password, db=self.db, charset='utf8')
            self.cursor = self.conn.cursor()
            return 0
        except Exception as e:
            print('[error] connect mysql error.' + str(e))
            return -1

    # query database table
    # 查询表
    def query_table(self, tablename):
        sql = "SELECT * FROM " + tablename
        try:
            self.cursor.execute(sql)
            row = self.cursor.fetchone()
            print(row)
            print(self.cursor.rowcount)
        except Exception as e:
            print("Failed to " + sql + str(e))

    # query porn information table
    # 查询影片信息表
    def query_table_torrent(self):
        self.query_table(self.table_torrent)

    # query pictures table
    # 查询图片表
    def query_table_pictures(self):
        self.query_table(self.table_pictures)

    # insert into [table_torrent] and return the primary key of the item just inserted
    # 插入到 [table_torrent] 返回刚插入的项的主键
    def insert_table_torrent(self, data='', name='', summary='', magnet=''):
        sql = "INSERT INTO " + self.table_torrent + " (data, name, summary, magnet) VALUES ('" + data + "', '" + \
              name + "', '" + summary + "', '" + magnet + "')"
        try:
            self.cursor.execute(sql)
            self.conn.commit()
            print("Successfully insert " + name + " into " + self.table_torrent)
        except Exception as e:
            print("Failed to " + sql + str(e))
        try:
            an_id = -1
            an_id = self.cursor.lastrowid
            if an_id != -1:
                return an_id
        except Exception as e:
            print("Failed to return last_insert_id." + str(e))

    # insert into [table_pictures]
    # 插入到 table_pictures
    def insert_table_pictures(self, an_id='', name=''):
        sql = "INSERT INTO " + self.table_pictures + " (an_id, name) VALUES ('" + str(an_id) + "', '" + name + "')"
        try:
            self.cursor.execute(sql)
            self.conn.commit()
            print("Successfully insert " + name + " into " + self.table_pictures)
        except Exception as e:
            print("Failed to " + sql + str(e))

    # close database
    def close_mysql(self):
        try:
            self.cursor.close()
            self.conn.close()
        except Exception as e:
            print("Failed to close mysql." + str(e))


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
        print("[" + str(id) + "] Successfully save the file to " + path)
        f.close()


# torrent and magnet-link page
# 种子/磁力链接页面
def Prase_Torrent(id, url):
    try:
        if (isProxy == True):
            req = requests.get(url, params=torrent_request_header, proxies=proxies_header)
        else:
            req = requests.get(url, params=torrent_request_header)
        
        soup = BeautifulSoup(req.content, "html.parser")
        torrent_content = soup.select('.uk-button ')
        torrent_content_num = len(torrent_content)
        if torrent_content_num == 0:
            print("[" + str(id) + "] No match torrent.")
            return ''
        for content in torrent_content:
            str_content = str(content)
            # matching magnet-link
            # 匹配磁力链接
            matchObj = re.search(r'magnet(.*?)"', str_content)
            if matchObj:
                magnet_link = 'magnet' + matchObj.group(1)
                return magnet_link
            else:
                # matching magnet-link failed
                # 匹配磁力链接失败
                print("[" + str(id) + "] No match: " + str_content)
                return ''
    except Exception as e:
        print("[" + str(id) + "] Prase_Torrent Exception: " + str(e))


# each post page
# 每个帖子页面
def Prase_Post(id, url, folder_name):
    try:
        # match data
        # 匹配日期
        data = ''
        matchObj = re.search(r'\[(.*?)\]', folder_name, re.M | re.I)
        if matchObj:
            data = matchObj.group(1)
        else:
            # match data failed
            # 匹配日期失败
            print("[" + str(id) + "] No match: " + folder_name)

        if (isProxy == True):
            req = requests.get(url, params=request_header, proxies=proxies_header)
        else:
            req = requests.get(url, params=request_header)

        encode_content = Encode_Conversion(req)
        soup = BeautifulSoup(encode_content, "html.parser")
        post_content = soup.select('div[id="read_tpc"]')
        post_content_num = len(post_content)
        if post_content_num == 0:
            print("[" + str(id) + "] No match post.")
            return

        # save text content
        # 保存文本内容
        summary = post_content[0].text
        str_content = str(post_content[0])

        # match magnet-link page
        # 匹配磁力
        magnet_link = ''
        matchObj = re.findall(r'href="(.*?)"', str_content)
        if matchObj:
            for obj in matchObj:
                magnet_link = Prase_Torrent(id, obj)
        else:
            # match magnet-link page failed
            # 匹配磁力失败
            print("[" + str(id) + "] No match: " + str_content)

        # insert the [insert_table_torrent] table of the database
        # 插入到 [insert_table_torrent] 表
        an_id = -1
        if folder_name != '' and magnet_link != '':
            an_id = mySQLCommand.insert_table_torrent(data=data, name=folder_name, summary=summary, magnet=magnet_link)

        if an_id != -1:
            # create a folder to save the picture
            # 创建保存图片的文件夹
            folder_path = save_path + '/' + str(an_id)
            folder = os.path.exists(folder_path)
            if not folder:
                os.makedirs(folder_path)
                print("[" + str(id) + "] Created folder " + str(an_id))

            # match pictures
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
                            # insert the [insert_table_pictures] table of the database
                            # 插入 [insert_table_pictures] 表
                            mySQLCommand.insert_table_pictures(an_id=an_id, name=img_name)
            else:
                # 匹配图片失败
                # match pictures failed
                print("[" + str(id) + "] No match: " + str_content)
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

        encode_content = Encode_Conversion(req)
        soup = BeautifulSoup(encode_content, "html.parser")
        post_list = soup.select('tr[class="tr3 t_one"] h3 a')
        post_num = len(post_list)
        if post_num == 0:
            print("[" + str(id) + "] No match post_list.")
            return
        for post in post_list:
            str_post = str(post)
            matchObj = re.match(r'(.*)href="(.*)" id=(.*)>(.*?)</a>', str_post, re.M | re.I)
            if matchObj:
                post_url = matchObj.group(2)
                post_name = matchObj.group(4)
                if post_name != '':
                    # match each post page
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
    # database command object 
    # # 数据库命令对象
    mySQLCommand = MySQLCommand()
    if mySQLCommand.connect_mysql() != -1:
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
        mySQLCommand.close_mysql()
