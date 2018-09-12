from __future__ import unicode_literals, print_function  # python2
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
import base64
import requests
from bs4 import BeautifulSoup
import datetime
from urllib import parse
import json
import random
from urllib.parse import quote
import  string
import time
# 当前的session会话对象
session = requests.session()

# 登录操作

user_website = ""
user_id = ""


def login(username, password):
    r = session.get("https://www.yiban.cn/login")
    soup = BeautifulSoup(r.text, "html.parser")
    ul = soup.find("ul", id="login-pr")
    # 从html当中获取私钥
    data_keys = ul['data-keys']
    # 从html当中获取时间
    data_keys_time = ul['data-keys-time']
    r = session.get("https://www.yiban.cn/captcha/index?" +
                    str(int(time.time())))
    r = session.get("https://www.yiban.cn/captcha/index?" +
                    (str(int(time.time()))))
    # 查找是否已经存在验证码
    with open("/Users/hdy/Desktop/yanzhengma.jpg", 'wb') as f:
            f.write(r.content)
    code = input("请输入验证码")
    # 获取到验证码
    # code = code.encode('unicode_escape')
    code = quote(code, safe = string.printable)
    print(code)
    encrypt_password = get_crypt_password(data_keys, password)
    form_data = {
        'account': username,
        'password': encrypt_password,
        'captcha': code,
        'keysTime': data_keys_time
    }
    print(form_data)
    # 进行模拟登陆
    r = session.post("https://www.yiban.cn/login/doLoginAjax", data=form_data,allow_redirects=False)
    # 获取到返回的json数据
    # print(r.text)
    login_json = json.loads(r.text)
    if(login_json['code'] == 200):
        print("模拟登陆成功")
        print(login_json)
        global user_website
        user_website = login_json['data']['url']
        global user_id
        user_id = user_website[user_website.index("_id")+4:]
        addFeed()
        # 循环四次.
        for i in range(4):
            addblog()
        addYiMiaoMiao()
    else:
        print("错误码:"+login_json['code']+" 原因:"+login_json['message'])
        if(login_json['code'] == '711'):
            r = session.get("https://www.yiban.cn/captcha/index?" +
                    (str(int(time.time()))))
            with open("/Users/hdy/Desktop/yanzhengma.jpg", 'wb') as f:
                f.write(r.content)
            code = input("请输入验证码")
            # 获取到验证码
            # code = code.encode('unicode_escape')
            code = quote(code, safe = string.printable)
            form_data = {
                'account': username,
                'password': encrypt_password,
                'captcha': code,
                'keysTime': data_keys_time
            }
            r = session.post("https://www.yiban.cn/login/doLoginAjax", data=form_data,allow_redirects=False)
            login_json = json.loads(r.text)
            if(login_json['code'] == 200):
                print("模拟登陆成功")
                print(login_json)
                user_website = login_json['data']['url']
                user_id = user_website[user_website.index("_id")+4:]
                addFeed()
                # 循环四次.
                for i in range(4):
                    addblog()
                addYiMiaoMiao()
            else:
                print("再次登录失败")
    # print(r.text)

# 密码进行rsa加密


def get_crypt_password(private_key, password):
    rsa = RSA.importKey(private_key)
    cipher = PKCS1_v1_5.new(rsa)
    ciphertext = encrypt(password, cipher)
    return ciphertext


def encrypt(msg, cipher):
    ciphertext = cipher.encrypt(msg.encode('utf8'))
    return base64.b64encode(ciphertext).decode('ascii')


# 发布动态(完成)
def addFeed():
    randomstr = str(random.randint(100, 99999))
    form_data = {
        "content": randomstr,
        "privacy": "0",
        "dom": ".js-submit"
    }
    # 自动发表动态
    r = session.post("http://www.yiban.cn/feed/add", data=form_data)
    print(r.text)
    post_json = json.loads(r.text)
    if(post_json['code'] == 200):
        feedId = str(post_json['data']['feedId'])
        print("获取到的动态id为:"+feedId)
        # 自动点赞
        session.post("http://www.yiban.cn/feed/up", data={"id": feedId})
        # 自动同情
        session.post("http://www.yiban.cn/feed/down", data={"id": feedId})
        # 自动发表评论
        comment_random = str(random.randint(100, 99999))
        session.post("http://www.yiban.cn/feed/createComment",
                     data={"id": feedId, "content": comment_random})
        print("动态相关的网薪完成.")
    else:
        print("动态发表错误....")

# 博文添加


def addblog():
    r = session.get("http://www.yiban.cn"+user_website)
    randomstr = str(random.randint(100, 99999))
    r = session.post("http://www.yiban.cn/blog/blog/addblog", data={"title": randomstr, "content": randomstr,
                                                                    "ranges": "1", "type": "1", "token": "64d41ba3222a4c4614fc33f594a6df4d", "ymm": "1", "dom": ".js-submit"})
    post_result = json.loads(r.text)
    if(post_result['code'] == 200):
        r = session.get(
            "http://www.yiban.cn/blog/blog/getBlogList?page=1&size=10&uid="+user_id)
        m_json = json.loads(r.text)
        if(m_json['code'] == 200):
            m_json = m_json["data"]["list"][0]
            blog_id = m_json['id']
            Mount_id = m_json['Mount_id']
            # 博文点赞
            session.get("http://www.yiban.cn/blog/blog/addlike/uid/" +
                        user_id+"/blogid/"+blog_id)
            # 评论博文
            # blogid: 12300216 oid: 18884862 mid: 48893712 reply_user_id: 0 reply_comment_id: 0 content: 123123123
            session.post("http://www.yiban.cn/blog/blog/addcomment/", data={
                         "blogid": blog_id, "oid": user_id, "mid": Mount_id, "reply_user_id": "0", "reply_comment_id": "0", "content": randomstr})
            print("博文发表成功")
        else:
            print("获取请求的博文错误...")

        # print("获得blogid:"+blogid)
    else:
        print("发表博文失败")

# 添加易喵喵


def addYiMiaoMiao():
    randomstr = str(random.randint(100, 99999))
    data_form = {"title": randomstr,
                 "content": randomstr, "kind": '8', "agree": 'true'}
    r = session.post("http://ymm.yiban.cn/article/index/add", json=data_form)
    print(r.text)


# 网站\客户端查看(个人/公共/机构账号)主页
def addPersonWebsite():
    # 查看个人
    session.get("http://www.yiban.cn/user/index/index/user_id/"+user_id)
    # 查看机构
    session.get("http://www.yiban.cn/school/index/id/5000090")
    # 查看公共
    session.get("http://www.yiban.cn/user/index/index/user_id/15977811")
    print("网站\客户端查看(个人/公共/机构账号)主页完成")

# try:
login('13216151732', 'h378759617')
# except Exception:
#     print("程序异常,登录失败.")
# addblog()
# str = """{"code":200,"message":"\u64cd\u4f5c\u6210\u529f","data":{"url":"\/user\/index\/index\/user_id\/18884862"}}"""
# m = json.loads(str)x
# print(m['code'])72c737918b586744d88347de2a58ee75
