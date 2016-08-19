# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pickle
import time
import sys
import re
reload(sys)
sys.setdefaultencoding('utf8')


class saveWeibo():
    def __init__(self):
        self.keyword = u""  #Keyword

    def getWeibo(self):
        infofile = open("SinaWeibo1.txt", 'wb')
        driver = webdriver.Chrome()
        driver.get('http://login.weibo.cn/login/')
        cookies = pickle.load(open("cookies.pkl", "rb"))
        for cookie in cookies:
            driver.add_cookie(cookie)
        driver.get('http://weibo.cn')
        keyword = self.keyword
        input_text = driver.find_element_by_name("keyword")
        input_text.send_keys(keyword)
        submit = driver.find_element_by_name('smblog') 
        submit.click()
        # comment = driver.find_elements_by_xpath("//a[@class='cc']")
        # content = driver.find_elements_by_xpath("//div[@class='c']")
        # all_comment_url = []               #存储所有文件URL
        # i = 0
        # j = 0
        # infofile.write(u'开始:\r\n')
        # print u'长度', len(content)
        # while i<len(content):
        #     #print content[i].text
        #     if (u'收藏' in content[i].text) and (u'评论' in content[i].text): #过滤其他标签
        #         print content[i].text
        #         infofile.write(u'微博信息:\r\n')
        #         infofile.write(content[i].text + '\r\n')
        #         div_id = content[i].get_attribute("id")
        #         print div_id
        #         while(1):  #存在其他包含class=cc 如“原文评论”
        #             url_com = comment[j].get_attribute("href")
        #             if ('comment' in url_com) and ('uid' in url_com):
        #                 print url_com
        #                 infofile.write(u'评论信息:\r\n')
        #                 infofile.write(url_com+'\r\n')
        #                 all_comment_url.append(url_com)    #保存到变量里
        #                 j = j + 1
        #                 break
        #             else:
        #                 j = j + 1
                    
        #     i = i + 1
        # nextPage = driver.find_element_by_link_text(u"下页")
        # nextPage.click()
        # infofile.close()
        print '\n'  
        print u'Start collection'  
        num = 1  
        while num <= 100:  
            url_wb = "http://weibo.cn"+ "/search/mblog?hideSearchFrame=&keyword=%E8%85%BE%E5%86%B2&page=" + str(num)  
            print url_wb  
            driver.get(url_wb)  
            #info = driver.find_element_by_xpath("//div[@id='M_DiKNB0gSk']/")  
            info = driver.find_elements_by_xpath("//div[@class='c']")
            # for value in info:
            #     if u'赞' not in value.text:
            #         continue
            #     else:
            #         print value.text
            #         print "-------------------------"

            for value in info:  
                # print value.text
                # print "-----------"
                # info = value.text  
  
                #跳过最后一行数据为class=c  
                #Error:  'NoneType' object has no attribute 'groups'  
                if u'赞' not in value.text:
                    print 'Go to next information', value.text, '\n' 
                    continue                    
                else:  
                    if (u'转发了') not in value.text:
                        print u'原创微博'  
                        infofile.write(u'原创微博\r\n')  
                    else:  
                        print u'转发微博'  
                        infofile.write(u'转发微博\r\n')  
                          
                    #获取最后一个点赞数 因为转发是后有个点赞数
                    print value.text
                    str1 = value.text.split(u" 赞")[-1]
                    print str1
                    print "``````````````````"
                    if str1:   
                        val1 = re.match(r'.*?(\d+)', str1, re.S).groups(1)
                        print u'点赞数: ', val1  
                        infofile.write(u'点赞数: ' + str(val1) + '\r\n')  
  
                    str2 = value.text.split(u" 转发")[-1]  
                    if str2:   
                        val2 = re.match(r'.*?(\d+)', str2, re.S).groups(1)
                        print u'转发数: ', val2  
                        infofile.write(u'转发数: ' + str(val2) + '\r\n')  
  
                    str3 = value.text.split(u" 评论")[-1]  
                    if str3:  
                        val3 = re.match(r'.*?(\d+)', str3, re.S).groups(1)
                        print u'评论数: ', val3  
                        infofile.write(u'评论数: ' + str(val3) + '\r\n')  
  
                    str4 = value.text.split(u" 收藏 ")[-1]  
                    flag = str4.find(u"来自")  
                    print u'时间: ' + str4[:flag]  
                    infofile.write(u'时间: ' + str4[:flag] + '\r\n')  
  
                    print u'微博内容:'  
                    print value.text[:value.text.rindex(u" 赞")]  #后去最后一个赞位置  
                    infofile.write(value.text[:value.text.rindex(u" 赞")] + '\r\n')  
                    infofile.write('\r\n')  
                    print '\n'  
            else:  
                print u'next page...\n'  
                infofile.write('\r\n\r\n')  
            num += 1  
            print '\n\n'  
        print '**********************************************'  

    def main(self):
        self.getWeibo()


test = saveWeibo()
test.main()

