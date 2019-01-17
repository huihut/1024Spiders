
# 代理时的请求头字典
proxt_novel_list_req_header = {
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
    'Referer': 'http://w3.afulyu.pw/pw/thread.php?fid=17&page=1',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 ' \
                  '(KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 OPR/57.0.3098.116'
}
# 代理信息
proxies = {'http': '127.0.0.1:1080', "https": "127.0.0.1:1080", }
base_url = "http://w3.jbzcjsj.pw/pw/"
save_path = "D:\\code\\Pycharm\\1024Spider\\torrent"
isProxy = True
fid = 3
page_start = 1
page_end = 245


if __name__ == "__main__":
    print("hello")