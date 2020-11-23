import requests
import json
import jsonpath
import time
import random
import os
import re
import subprocess

proxies={
    "http":"127.0.0.1:7890"
}
headers = {
    'user-agent': "Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1",
    'Connections': 'keep-alive'
}

'''
最智障的地方，获取签名
Thx for https://github.com/yalarc/GetDouYinApplication
'''
def generateSignature(user_id):
    p = subprocess.run('node fuck-byted-acrawler.js %s' % user_id,shell=True,stdout=subprocess.PIPE)
    # return p.readlines()[0]
    return str(p.stdout).replace('b\'','').replace('\'','')

'''
由分享链接获得真实链接
'''
def get_real_address(shareurl):
    requests.packages.urllib3.disable_warnings()
    if shareurl.find('v.douyin.com') < 0:
        return shareurl
    res = requests.get(shareurl, headers=headers, allow_redirects=False, verify=False)
    return res.headers['Location'] if res.status_code == 302 else None

'''
获取 user_id 和 sec_uid
'''
def get_user_id_sec_uid(realurl):
    patOfUserId = "/user/(.*?)\?"
    patOfSecId = "sec_uid=(.*?)&"
    user_id = re.compile(patOfUserId,re.S).findall(realurl)[0]
    sec_uid = re.compile(patOfSecId,re.S).findall(realurl)[0]
    return user_id,sec_uid

'''
获取作品数量
'''
def get_aweme_count(sec_uid):
    originalurl = "https://www.iesdouyin.com/web/api/v2/user/info/?sec_uid="+str(sec_uid)
    response = requests.get(originalurl, headers=headers, timeout=10).text
    resp = json.loads(response)
    aweme_count = str(jsonpath.jsonpath(resp, '$..aweme_count')).replace('[', '').replace(']', '')
    return aweme_count
    print(aweme_count)

'''
获取最最最真实地址
'''
def get_real_real_url(max_cursor,sec_uid,signature):
    url = 'https://www.iesdouyin.com/web/api/v2/aweme/post/?sec_uid='+sec_uid+'&count=21&max_cursor=' + str(
        max_cursor) + '&aid=1128&_signature=' + signature + '&dytk='
    return url

'''
Thx for https://www.cnblogs.com/cherish-hao/p/12828027.htmls
'''
class Douyin:
    def page_num(self,sec_uid,random_field,max_cursor):
        # 网址的主体
        url = 'https://www.iesdouyin.com/web/api/v2/aweme/post/?sec_uid='+sec_uid+'&count=21&max_cursor=' + str(max_cursor) + '&aid=1128&_signature=' + random_field + 'dytk='

        response = requests.get(url, headers=headers, timeout=10).text
        # 转换成json数据
        resp = json.loads(response)
        # 提取到max_cursor
        max_cursor = resp.get('max_cursor')
        # 遍历
        for data in resp['aweme_list']:
            # print(data)
            nickname = str(jsonpath.jsonpath(data, '$..nickname')).replace('[\'', '').replace('\']', '')
            print(nickname)
            # 视频简介
            video_title = data['desc']
            # 使用jsonpath语法提取paly_addr
            video_url = jsonpath.jsonpath(data, '$..play_addr')
            for a in video_url:
                # 提取出来第一个链接地址
                video_realurl = a['url_list'][1]
            # 请求视频
            video = requests.get(video_realurl, headers=headers, timeout=10).content
            file_name = str(video_title) + '.mp4'
            if os.path.exists(nickname):
                os.chdir(nickname)
            else:
                os.mkdir(nickname)
                os.chdir(nickname)
            with open(file_name, 'wb') as f:

                print('正在下载：', file_name)
                print(video_realurl)
                f.write(video)
                time.sleep(random.randint(9,14))
                os.chdir('..')
        return max_cursor

if __name__ == '__main__':
    shareurl = str(input("shareurl:"))
    realurl = get_real_address(shareurl)
    print(realurl)
    user_id, sec_uid = get_user_id_sec_uid(realurl)
    print(user_id,sec_uid)
    signature = str(generateSignature(user_id))
    print(signature)
    douyin = Douyin()
    max_cursor = douyin.page_num(sec_uid=sec_uid,random_field=signature,max_cursor=0)
    # 判断停止构造网址的条件
    while max_cursor != 0:
        max_cursor=douyin.page_num(sec_uid=sec_uid,random_field=signature,max_cursor=max_cursor)