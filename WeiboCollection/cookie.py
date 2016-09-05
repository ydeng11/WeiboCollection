import requests
import base64
import json
import ConfigParser

class getCookies():
    def __init__(self):


    def login(self,username, password):
        username = base64.b64encode(username.encode('utf-8')).decode('utf-8')
        postData = {
            "entry": "sso",
            "gateway": "1",
            "from": "null",
            "savestate": "30",
            "useticket": "0",
            "pagerefer": "",
            "vsnf": "1",
            "su": username,
            "service": "sso",
            "sp": password,
            "sr": "1440*900",
            "encoding": "UTF-8",
            "cdult": "3",
            "domain": "sina.com.cn",
            "prelt": "0",
            "returntype": "TEXT",
        }
        loginURL = r'https://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.15)'
        session = requests.Session()
        res = session.post(loginURL, data = postData)
        jsonStr = res.content
        info = json.loads(jsonStr)
        if info["retcode"] == "0":
            print("Log in sucessfully!")
            cookies = session.cookies.get_dict()
            cookies = [key + "=" + value for key, value in cookies.items()]
            cookies = "; ".join(cookies)
            #Prepare the cookies pool
            f = open('cookies.txt', 'a')
            f.write(cookies)
            f.write("\n")
            f.close
            session.headers["cookie"] = cookies
        else:
            print("Error： %s" % info["reason"])
        return session