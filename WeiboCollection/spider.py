# -*- coding: utf-8 -*-
import cookielib
import urllib2
import ConfigParser
import requests
import json
import base64
import urllib2
import requests.packages.urllib3
import re
from datetime import datetime
from datetime import timedelta
requests.packages.urllib3.disable_warnings()
import logger
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import cookie
import random
import MySQLdb
import time


class weibo():

	def __init__(self):
		self.baseurl = "http://s.weibo.com/weibo/%25E8%2585%25BE%25E5%2586%25B2&typeall=1&suball=1&timescope=custom:"
		# self.starttime = "2015-08-30-12"
		self.starttime = "2015-9-14-12"
		self.endtime = "2016-08-30-12"
		self.table = "weibo_tc"
		self.logger = logger.Logger('log.txt', "myblog").getlog()
		# cf = ConfigParser.ConfigParser()
		# cf.read('config.conf')
		# self.userpool = cf.items("db")
		with open ("cookies.txt", "rb") as f:
			cookies = f.read()
		self.cookie_list = cookies.split("\n")
		with open("user_agent.txt","rb") as f:
			user_agent = f.read()
		self.ua_list = user_agent.split('\n')
		self.getCookies = cookie.getCookies()

	# def login(self,username, password):
	# 	username = base64.b64encode(username.encode('utf-8')).decode('utf-8')
	# 	postData = {
	# 		"entry": "sso",
	# 		"gateway": "1",
	# 		"from": "null",
	# 		"savestate": "30",
	# 		"useticket": "0",
	# 		"pagerefer": "",
	# 		"vsnf": "1",
	# 		"su": username,
	# 		"service": "sso",
	# 		"sp": password,
	# 		"sr": "1440*900",
	# 		"encoding": "UTF-8",
	# 		"cdult": "3",
	# 		"domain": "sina.com.cn",
	# 		"prelt": "0",
	# 		"returntype": "TEXT",
	# 	}
	# 	loginURL = r'https://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.15)'
	# 	session = requests.Session()
	# 	res = session.post(loginURL, data = postData)
	# 	jsonStr = res.content
	# 	info = json.loads(jsonStr)
	# 	if info["retcode"] == "0":
	# 		print("Log in sucessfully!")
	# 		cookies = session.cookies.get_dict()
	# 		cookies = [key + "=" + value for key, value in cookies.items()]
	# 		cookies = "; ".join(cookies)
	# 		#Prepare the cookies pool
	# 		f = open('cookies.txt', 'a')
	# 		f.write(cookies)
	# 		f.write("\n")
	# 		f.close
	# 		session.headers["cookie"] = cookies
	# 	else:
	# 		print("Error： %s" % info["reason"])
	# 	return session

	def clean(self,word):
		word = re.sub(r"<.*?em.*?>",r"", word)
		word = re.sub(r"\\n|\\t|",r"", word)
		word = re.sub(r"<\\/p>",r"", word)
		word = re.sub(r"<img.*?>",r"",word)
		word = re.sub(r"<a href.*?>", r"", word)
		word = re.sub(r"<i class.*?>", r"", word)
		word = re.sub(r"c<\\.*?>", r"", word)
		word = re.sub(r"<.*?>", r"", word)
		word.strip()
		return word

	def getUrl(self):
		starttime = self.starttime
		endtime = self.endtime
		# get the baseurl manually and put it in init
		baseurl = self.baseurl
		time_format = "%Y-%m-%d-%H"
		end = datetime.strptime(endtime, time_format)
		start = datetime.strptime(starttime, time_format)
		differences = end - start
		# differences = endtime - starttime
		days = differences.days
		urllist = []
		while days > 0:
			if days>15:
				interval = 15
				days -= interval
				end  = start + timedelta(days=interval)
				initUrl = baseurl + str(start).split(" ")[0]+"-12" +":" +str(end).split(" ")[0]+"-12" + "&Refer=g"
				urllist.append(initUrl)
				start = end
			else:
				interval = days
				days = 0
				end  = start + timedelta(days=interval)
				initUrl = baseurl + str(start).split(" ")[0]+"-12" +":" +str(end).split(" ")[0]+"-12" + "&Refer=g"
				urllist.append(initUrl)
				start = end
		return urllist

	# def getHtml(self, username, password, url):
	#     session = self.login(username, password)
 #    	r = session.get(url)
 #    	return r.content


	def getPageNumber(self, html):
		page_pattern = re.compile("layer_menu_list W_scroll(.*?)W_ficon ficon_arrow_down S_ficon", re.S)
		page_box = re.findall(page_pattern, html)
		#Get the total page number
		page_urls = re.compile("<a href")
		# print page_box
		pages = re.findall(page_urls, page_box[0])
		page_number =  len(pages)-1
		return page_number

	def savetomysql(self, table, data):
			try:
				db = MySQLdb.connect('localhost','root','891105','mysql')
				cur = db.cursor()
			except MySQLdb.Error, e:
				print "The error found in connnecting database%d: %s" % (e.args[0], e.args[1])
			try:
				db.set_character_set('utf8')
				cols = ', '.join(str(v) for v in data.keys())
				values = '"'+'","'.join(str(v) for v in data.values())+'"'
				sql = "INSERT INTO %s (%s) VALUES (%s)" % (table, cols, values) #the primary key is photo_id
				# print sql
				try:
					result = cur.execute(sql)
					db.commit()
					#Check the result of command execution
					if result:
						print "This data is imported into database."
					else:
						return 0
				except MySQLdb.Error,e:
					 #rollback if error
					db.rollback()
					 #duplicate primary key
					if "key 'PRIMARY'" in e.args[1]:
						print "Data Existed"
					else:
						print "Insertion faied, reason is %d: %s" % (e.args[0], e.args[1])
			except MySQLdb.Error,e:
				print "Error found in database, reason is %d: %s" % (e.args[0], e.args[1])


	def getandsaveInformation(self, html):
		table = self.table
		pattern = re.compile("WB_cardwrap S_bg2 clearfix(.*?)feed_list_repeat", re.S)
		matches = re.findall(pattern, html)
		for match in matches:
			content = match
			name_box = re.compile('nick-name.{3}(.*?)"', re.S)
			raw_name = re.search(name_box, content)
			raw_name = raw_name.group(1).rstrip('\\')
			try:
				name = raw_name.decode('unicode_escape')
			except:
				Exception
				continue
			# print name
			comment_box = re.compile('comment_txt.*?nick.*?>(.*?)<div',re.S)
			raw_comment = re.search(comment_box, content)
			raw_comment = raw_comment.group(1)

			raw_comment = self.clean(raw_comment)
			try:
				comment = raw_comment.decode('unicode_escape')
			except:
				Exception
				continue
			time_box = re.compile('feed_list_item_date.*?>(.*?)<', re.S)
			raw_time = re.search(time_box, content)
			time = raw_time.group(1)

			infor_box = re.compile("line S_line1.*?<\\\/span", re.S)
			raw_infor = re.findall(infor_box, content)
			p_unciode = re.compile("(\\u[a-f,0-9]{4})")
			information = {
							"user_name": name,
							"content" : comment,
							"time": time,
							"saved" : 0,
							"forwarded" : 0,
							"comments" : 0,
							"likes" : 0
							}
			for infor in raw_infor:
				data_word = ""
				words = re.findall(p_unciode, infor)
				number = re.sub(p_unciode, "", infor)
				if len(words) > 0:
					for word in words:
						data_word =  data_word + (str("\\"+word).decode("unicode_escape"))
				else:
					data_word = u"赞"
				data_number = re.match(r'line S_line1\\">.*?<em>(\d+)', number, re.S)
				# try:
				# 	print data_number.group(1)
				# except Exception,e:
				# 	print str(e)
				# if len[data_word] == 0:
				# 	data_word = u"赞"
				if data_number is None:
					print data_word + " has no value"
				else:
					if data_word == u"收藏":
						information.update({"saved" : data_number.group(1)})
					elif data_word == u"转发":
						information.update({"forwarded" : data_number.group(1)})
					elif data_word == u"评论":
						information.update({"comments" : data_number.group(1)})
					else:
						information.update({"likes" : data_number.group(1)})
			self.savetomysql(table, information)
	
	# def re_login(self):
	# 	cookie_list = self.cookie_list
	# 	ua_list = self.ua_list
	# 	getCookies = self.getCookies
	# 	logger = self.logger
	# 	#loop through the user pool
	# 	session = requests.Session()
	# 	i = 0
	# 	while len(cookie_list)>0:
	# 		try:
	# 			cookie = cookie_list[0]
	# 			loc_ua = random.randint(0, len(ua_list)-1)
	# 			ua = ua_list[loc_ua]
	# 			session.headers["cookie"] = cookie
	# 			session.headers["Usea-agent"] = ua
	# 			r = session.get(url)

	# 			break
	# 		except Exception, e:
	# 			logger.debug(repr(e))
	# 			logger.debug( str(i) + " cookie has been out of service")
	# 			cookie_list[0] = ""
	# 			if len(cookie_list) == 0:
	# 				logger.info("The cookie pool has been used up and program stop")
	# 				logger.info("Produce some cookies")
	# 				cookie_list = getCookies.login()
	# 		i += 1
	# 		if i == 50:
	# 			logger.info("There is no valid cookies can be produced!")
	# 			sys.exit("The cookies doesn't work any more!")
	# 	return session

		# use urllib2 to get the html of page
	# def main(self):
	# 	logger = self.logger
	# 	table = self.table
	# 	cookie_list = self.cookie_list
	# 	ua_list = self.ua_list
	# 	#loop through the cookie pool and urllist
	# 	urllist = self.getUrl()
	# 	getCookies = self.getCookies
	# 	for url in urllist:
	# 		logger.info("Crawling " + url)
	# 		loc_time = 0
	# 		#get the cookie from the cookie_list and delete the one which is invalid
	# 		#if the cookie_list is empty, reproduce the cookies until a certain time
	# 		while len(cookie_list) > 0:
	# 			try:
	# 				cookie = cookie_list[0]
	# 				loc_ua = random.randint(0, len(ua_list)-1)
	# 				ua = ua_list[loc_ua]
	# 				headers = {
	# 							"cookies": cookie,
	# 							"User-agent": ua
	# 				}
	# 				rq = urllib2.Request(url, headers = headers)
	# 				html = urllib2.urlopen(rq).read()
	# 				print html
	# 				break
	# 				# break the loop if the content is found
	# 				pattern = re.compile("WB_cardwrap S_bg2 clearfix(.*?)feed_list_repeat", re.S)
	# 				matches = re.findall(pattern, html)
	# 				if len(matches) > 0:
	# 					break
	# 				logger.info(cookie_list[0] + "is not valid any more")
	# 				cookie_list[0] = ""
	# 				if len(cookie_list) == 0:
	# 					cookie_list = getCookies.login()
	# 				logger.info("Reproduce cookie list")
	# 				loc_iteration += 1
	# 				if loc_iteration == 200:
	# 					logger.info("No valid cookies can be produced and stop program!")
	# 					sys.exit()
	# 			except Exception, e:
	# 				logger.debug(repr(e))
	# 		# print html
	# 		page_number = self.getPageNumber(html)
	# 		logger.info(url + " has %s pages" %page_number)
	# 		for i in range(1,page_number+1):
	# 			new_url = url + "&page=" +str(i)
	# 			logger.info("crawling page " + str(i))
	# 			content = session.get(url)
	# 			data = self.getInformation(content)
	# 			self.savetomysql(table, data)
	# 			logger.info("The page"+ str(i) +  "has been saved")

	# Use requests to get the html of page
	# def main(self):
	# 	logger = self.logger
	# 	table = self.table
	# 	cookie_list = self.cookie_list
	# 	ua_list = self.ua_list
	# 	#loop through the cookie pool and urllist
	# 	urllist = self.getUrl()
	# 	session = requests.Session()
	# 	for url in urllist:
	# 		logger.info("Crawling " + url)
	# 		loc_cookie = 0
	# 		cookie = cookie_list[loc_cookie]
	# 		print cookie
	# 		while loc_cookie <  len(cookie_list):
	# 			print "------"
	# 			try:
	# 				loc_ua = random.randint(0, len(ua_list)-1)

	# 				ua = ua_list[loc_ua]
	# 				print ua
	# 				session.headers["cookie"] = cookie
	# 				session.headers["Usea-agent"] = ua
	# 				r = session.get(url)
	# 				print r.content
	# 				break
	# 			except Exception, e:
	# 				logger.debug(repr(e))
	# 				session = self.re_login()
	# 				r = session.get(url)
	# 		html = r.content
	# 		# print html
	# 		page_number = self.getPageNumber(html)
	# 		logger.info(url + " has %s pages" %page_number)
	# 		for i in range(1,page_number+1):
	# 			new_url = url + "&page=" +str(i)
	# 			logger.info("crawling page " + str(i))
	# 			content = session.get(url)
	# 			data = self.getInformation(content)
	# 			self.savetomysql(table, data)
	# 			logger.info("The page"+ str(i) +  "has been saved")

	def main(self):
		username = "dengyujun@ymail.com"
		password = "631225dyj!"
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
			print("登录成功")
			# 把cookies添加到headers中，必须写这一步，否则后面调用API失败
			cookies = session.cookies.get_dict()
			cookies = [key + "=" + value for key, value in cookies.items()]
			cookies = "; ".join(cookies)
			ua = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.77.4 (KHTML, like Gecko) Maxthon/4.2.3"
			# print cookies
			session.headers["cookie"] = cookies
			session.headers["User-agent"] = ua
			session.get(loginURL)
		else:
			print("登录失败，原因： %s" % info["reason"])
		logger = self.logger
		table = self.table
		# cookie_list = self.cookie_list
		# ua_list = self.ua_list
		#loop through the cookie pool and urllist
		urllist = self.getUrl()
		for url in urllist:
			logger.info("Crawling " + url)
			r = session.get(url)
			html = r.content
			# print html
			page_number = self.getPageNumber(html)
			logger.info(url + " has %s pages" %page_number)
			for i in range(1,page_number+1):
				new_url = url + "&page=" +str(i)
				logger.info("crawling page " + new_url)
				r = session.get(new_url)
				self.getandsaveInformation(str(r.content))
				logger.info("The page "+ str(i) +  " has been saved")
				time.sleep(random.randint(5,10))
			# time.sleep(2)

test = weibo()
test.main()