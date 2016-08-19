# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pickle
import time
import sys
reload(sys)
sys.setdefaultencoding('utf8')

class saveCookies():
    def __init__(self):
        print "start acquiring cookies"
        self.username = "your weibo username"
        self.password = "your password"

    def getCookies(self):

        driver = webdriver.Chrome()
        driver.get('http://login.weibo.cn/login/')
        driver.delete_all_cookies()
        if driver.find_element_by_name('mobile'):
            driver.find_element_by_name('mobile').send_keys(self.username)
            driver.find_element_by_xpath("//input[@type='password']").send_keys(self.password)
            if driver.find_element_by_name("code"):
                while True:
                    val = driver.find_element_by_name("code")
                    # print val.get_attribute("value")
                    time.sleep(5)
                    if val and len(val.get_attribute("value"))>0:
                        code = val.get_attribute("value")
                        val.clear()
                        driver.find_element_by_name("code").send_keys(code)
                        break
                    pass
                pass
            driver.find_element_by_name('submit').click()
            print 'log in'
        
        wait = WebDriverWait(driver, 10)
        element = wait.until(EC.presence_of_element_located((By.NAME,'smblog')))
        if element:
            pickle.dump(driver.get_cookies() , open("cookies.pkl","wb"))
            print "The cookies is saved."
            driver.close()

# test = saveCookies()
# test.getCookies()

