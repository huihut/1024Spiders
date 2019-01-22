#!/usr/bin/python3
# -*- coding: UTF-8 -*-
import urllib
import urllib.parse
import urllib.request
from urllib.request import urlopen
import requests
import threading
from bs4 import BeautifulSoup
import re
from urllib.parse import urlencode, parse_qs, urlsplit, urlunsplit


# 转换编码
def encodeConversion(req):
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


# 设置网络请求的参数
def set_query_parameter(url, param_name, param_value):
    """Given a URL, set or replace a query parameter and return the
    modified URL.

    >>> set_query_parameter('http://example.com?foo=bar&biz=baz', 'foo', 'stuff')
    'http://example.com?foo=stuff&biz=baz'

    """
    scheme, netloc, path, query_string, fragment = urlsplit(url)
    query_params = parse_qs(query_string)

    query_params[param_name] = [param_value]
    new_query_string = urlencode(query_params, doseq=True)

    return urlunsplit((scheme, netloc, path, new_query_string, fragment))


# 每个小说帖子页面
def praseHtml(req_url , headers, path):
    try:
        # 请求当前章节页面  params为请求参数
        global isProxy
        global proxies
        if (isProxy == True):
            req = requests.get(req_url, params=headers, proxies=proxies)
        else:
            req = requests.get(req_url, params=headers)

        # 转换编码
        encode_content = encodeConversion(req)
        # soup转换
        soup = BeautifulSoup(encode_content, "html.parser")
        # 获取章节名称
        section_name = soup.select('#subject_tpc')[0].text
        # 获取章节文本
        section_text = soup.select('#read_tpc')[0].text
        result = section_name + '\n' + section_text
        result = result.replace('　　', '\n  ')

        if result != "" and section_name != "":
            savePath = path + "\\" + str(section_name).replace(u'\0', u'').replace(u'\t', u'') + ".txt"
            f = open(savePath, "w", encoding='utf-8')
            f.write(result)
    except ValueError:
        print("ValueError: 传入无效的参数" + req_url)
    except IndexError:
        print("IndexError: 没有此网页索引：" + req_url)
    except IOError:
        print("IOError: 没有找到文件或读取文件失败" + req_url)
    except Exception as e:
        print("Exception: 存在异常" + e + req_url)
    else:
        # 内容写入文件成功
        print(req_url, end='')
        f.close()


# 成人小说帖子列表页面
def novelList(directory_url, fid, page , chapter_url, headers, path):
    # content_url = directory_url + '?fid='+str(fid)+"&page="+str(page)

    directory_url = set_query_parameter(directory_url, 'fid', fid)
    directory_url = set_query_parameter(directory_url, 'page', page)

    print(directory_url + ' start downloading')

    # 请求当前章节页面  params为请求参数
    global isProxy
    if(isProxy == True):
        req = requests.get(directory_url, params=headers, proxies=proxies)
    else:
        req = requests.get(directory_url, params=headers)

    # 转换编码
    encode_content = encodeConversion(req)

    # soup转换
    soup = BeautifulSoup(encode_content, "html.parser")
    # 获取章节名称
    section_list = soup.select('.tr3 h3 a')
    section_num = len(section_list)
    if section_num == 0:
        print("目录页面不正确，无法找到匹配项！")
        return -1
    for section in section_list:
        str_section = str(section)
        # php网页的匹配
        matchObj_act = re.match(r'(.*)a_ajax_(.*)">(.*?)</a>', str_section, re.M | re.I)
        if matchObj_act:
            section_sub = matchObj_act.group(2)  # 章节的标识
            section_name = matchObj_act.group(3)  # 章节的名字
            global php_chapter_url  # php的章节URL
            php_chapter_url = set_query_parameter(php_chapter_url, 'tid', section_sub)
            php_chapter_url = set_query_parameter(php_chapter_url, 'fpage', page)
            praseHtml(php_chapter_url, headers, path)
            prase_num = section_list.index(section) + 1
            print(' [ ' + "{:.1f}".format(prase_num / section_num * 100) + '% chapter completed ]  ')
        else:
            # html网页的匹配
            matchObj = re.match(r'(.*)href="htm_data(.*)" id=(.*)>(.*?)</a>', str_section, re.M | re.I)
            if matchObj:
                section_sub = matchObj.group(2)  # 章节的标识
                section_name = matchObj.group(4)  # 章节的名字
                # 传入html章节的URL
                praseHtml(chapter_url + section_sub, headers, path)
                prase_num = section_list.index(section) + 1
                print(' [ ' + "{:.1f}".format(prase_num / section_num * 100) + '% chapter completed ]  ')
            else:
                # 匹配失败
                print("No match: " + str_section)
                return -1


def spider(directory_url, fid, page_start, page_end, chapter_url, novel_list_req_header, path):
    page_num = abs(page_end-page_start)+1
    for each_page in range(page_start, page_end):
        list_return = novelList(directory_url, fid, each_page, chapter_url, novel_list_req_header, path)
        if list_return == -1:
            break
        prase_num = abs(each_page - page_start)+1
        print(' [ ' + "{:.1f}".format(prase_num/page_num*100) + '% page completed ] ')


if __name__ == "__main__":
    # 请求头字典
    novel_list_req_header = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
        'Cache-Control': 'no-cache',
        'Connection': 'keep - alive',
        'Cookie':'UM_distinctid=16574ce27ac246-04d3d1f1292635-9393265-1fa400-16574ce27aeff; aafaf_readlog'\
                 '=%2C1245721%2C; aafaf_ol_offset=35448165; CNZZDATA1261158850=1879378976-1535261549-%7C1535279419;'\
                 ' aafaf_lastpos=F17; aafaf_threadlog=%2C18%2C14%2C15%2C16%2C17%2C; aafaf_lastvisit=7839%09153528353'\
                 '2%09%2Fpw%2Fthread.php%3Ffid%3D17%26page%3D2',
        'Host': 'w3.afulyu.pw',
        'Pragma': 'no-cache',
        # 'Proxy-Connection': 'keep-alive',
        'Referer': 'http://w3.afulyu.pw/pw/thread.php?fid=17&page=1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'\
                      ' Chrome/68.0.3440.106 Safari/537.36'
    }
    # 代理时的请求头字典
    proxt_novel_list_req_header = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
        'Cache-Control': 'no-cache',
        # 'Connection': 'keep - alive',
        'Cookie': '__cfduid=d7e5c699ef4d6599ef01239424b0e6cd71547705542; aafaf_lastvisit=0%091547705542%09%2Fpw%2Findex.php%3F;' \
                  ' UM_distinctid=1685a707030539-0653970bbabd2b-46564b55-1fa400-1685a707031a0a; ' \
                  'CNZZDATA1261158850=317005769-1547705297-%7C1547705297',
        'Host': 'w3.jbzcjsj.pw',
        'Pragma': 'no-cache',
        'Proxy-Connection': 'keep-alive',
        'Referer': 'http://w3.afulyu.pw/pw/thread.php?fid=17&page=1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 ' \
                      '(KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 OPR/57.0.3098.116'
    }

    global php_chapter_url
    global isProxy
    global proxies
    directory_url = "http://w3.afulyu.pw/pw/thread.php"                 # 小说目录url
    html_chapter_url = 'http://w3.afulyu.pw/pw/htm_data'                # 每篇小说的html页面
    php_chapter_url = 'http://w3.afulyu.pw/pw/read.php'                 # 每篇小说的php页面
    save_path = 'D:\\code\\Pycharm\\1024Spider\\novel'                 # 保存在本地的路径
    proxies = {'http': '127.0.0.1:1080', "https": "127.0.0.1:1080", }   # 代理信息
    fid = 17            # 网站帖子类型，17代表小说
    page_start = 1      # 小说目录开始页面
    page_end = 940      # 小说目录结束页面
    isProxy = False      # 是否设置代理

    spider(directory_url, fid, page_start, page_end, html_chapter_url, proxt_novel_list_req_header, save_path)
    