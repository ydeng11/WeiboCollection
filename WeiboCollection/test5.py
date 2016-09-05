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

class weibo():

	def __init__(self):
		self.baseurl = "http://s.weibo.com/weibo/%25E8%2585%25BE%25E5%2586%25B2&typeall=1&suball=1&timescope=custom:"
		self.starttime = "2015-08-30-12"
		self.endtime = "2016-08-30-12"
		self.table = "weibo_tc"
		self.logger = logger.Logger('log.txt', "myblog").getlog()
		cf = ConfigParser.ConfigParser()
		cf.read('config.conf')
		# username = cf.options("db")
		self.userpool = cf.items("db")

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
		print page_box
		pages = re.findall(page_urls, page_box[0])
		page_number =  len(pages)-1
		return page_number

	def getInformation(self, html):
		pattern = re.compile("WB_cardwrap S_bg2 clearfix(.*?)feed_list_repeat", re.S)
		matches = re.findall(pattern, html)
		for match in matches:
			content = match
			name_box = re.compile('nick-name.{3}(.*?)"', re.S)
			raw_name = re.search(name_box, content)
			raw_name = raw_name.group(1).rstrip('\\')
			name = raw_name.decode('unicode_escape')
			# print name
			comment_box = re.compile('comment_txt.*?nick.*?>(.*?)<div',re.S)
			raw_comment = re.search(comment_box, content)
			raw_comment = raw_comment.group(1)

			raw_comment = self.clean(raw_comment)
			comment = raw_comment.decode('unicode_escape')

			infor_box = re.compile("line S_line1.*?<\\\/span", re.S)
			raw_infor = re.findall(infor_box, content)
			p_unciode = re.compile("(\\u[a-f,0-9]{4})")
			information = {
							u"user_name": name,
							u"content" : comment,
							u"saved" : 0,
							u"forwarded" : 0,
							u"comments" : 0,
							u"likes" : 0
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
						information.update({u"saved" : data_number.group(1)})
					elif data_word == u"转发":
						information.update({u"forwarded" : data_number.group(1)})
					elif data_word == u"评论":
						information.update({u"comments" : data_number.group(1)})
					else:
						information.update({u"likes" : data_number.group(1)})

			return information

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

	def re_login(self):
		login_infor = self.userpool
		#loop through the user pool
		i = 0
		while i < len(login_infor):
			try:
				loc_user = i
				username = login_infor[loc_user][0]
				password = login_infor[loc_user][1]
				session = self.login(username, password)
				break
			except Exception, e:
				i += 1
				logger.debug(repr(e))
				logger.debug( str(i) + " accounts has been blocked or invalidated")
		if i == len(login_infor):
			logger.info("The user pool has been used up and program stop")
			sys.exit("Please check log file")
		return session

	# def main(self):
	# 	logger = self.logger
	# 	table = self.table
	# 	login_infor = self.userpool
	# 	#loop through the user pool
	# 	url = 'http://s.weibo.com/weibo/%25E8%2585%25BE%25E5%2586%25B2&typeall=1&suball=1&timescope=custom:2015-08-30-12:2015-08-30-12&Refer=g'
	# 	try:
	# 		loc_user = 0
	# 		username = login_infor[loc_user][0]
	# 		password = login_infor[loc_user][1]
	# 		session = self.login(username, password)
	# 		r = session.get(url)
	# 		print r.content
	# 		print "-----------"
	# 	except Exception, e:
	# 		session = re_login()
	# 		logger.debug(repr(e))
	# 	loc_url = 0
	# 	urllist = self.getUrl()
	# 	for url in urllist:
	# 		logger.info("Crawling " + url)
	# 		try:
	# 			r = session.get(url)
	# 			print r.content
	# 			print "-----------"
	# 		except Exception, e:
	# 			logger.debug(repr(e))
	# 			session = re_login()
	# 			r = session.get(url)
	# 		html = r.content
	# 		print html
	# 		page_number = self.getPageNumber(html)
	# 		logger.infor(url + " has %s pages" %page_number)
	# 		for i in range(1,page_number+1):
	# 			new_url = url + "&page=" +str(i)
	# 			logger.debug(new_url)
	# 			content = session.get(url)
	# 			data = self.getInformation(content)
	# 			self.savetomysql(table, data)
	# 			logger.info("The data has been saved")

	def main(self):
		logger = self.logger
		table = self.table
		login_infor = self.userpool
		#loop through the user pool
		url = 'http://s.weibo.com/weibo/%25E8%2585%25BE%25E5%2586%25B2&typeall=1&suball=1&timescope=custom:2015-08-30-12:2015-09-14-12&Refer=g'
		# session = self.login("dengyujun@ymail.com", "891105xy!")
		# r = session.get(url)
		# print r.content
		loc_user = 0
		username = login_infor[loc_user][0]
		password = login_infor[loc_user][1]
		print username
		print password
		session = self.login(username, password)
		test = session.get("https://weibo.com.cn")
		r = session.get(url)
		print r.content
		# try:
		# 	loc_user = 0
		# 	username = login_infor[loc_user][0]
		# 	password = login_infor[loc_user][1]
		# 	print username
		# 	print password
		# 	session = self.login(username, password)
		# 	r = session.get(url)
		# 	print r.content
		# 	print "-----------"
		# except Exception, e:
		# 	session = re_login()
		# 	logger.debug(repr(e))
		# loc_url = 0
		# urllist = self.getUrl()
		# for url in urllist:
		# 	logger.info("Crawling " + url)
		# 	try:
		# 		r = session.get(url)
		# 		print r.content
		# 		print "-----------"
		# 	except Exception, e:
		# 		logger.debug(repr(e))
		# 		session = re_login()
		# 		r = session.get(url)
		# 	html = r.content
		# 	print html
		# 	page_number = self.getPageNumber(html)
		# 	logger.infor(url + " has %s pages" %page_number)
		# 	for i in range(1,page_number+1):
		# 		new_url = url + "&page=" +str(i)
		# 		logger.debug(new_url)
		# 		content = session.get(url)
		# 		data = self.getInformation(content)
		# 		self.savetomysql(table, data)
		# 		logger.info("The data has been saved")
		
		# print len(login_infor)

test = weibo()
test.main()
# url = 'http://s.weibo.com/weibo/%25E8%2585%25BE%25E5%2586%25B2&typeall=1&suball=1&timescope=custom:2016-08-01-0:2016-09-01-0&Refer=g'    
# # session = login()
# session = test.login('dengyujun@ymail.com', '891105xy!')
# r = session.get(url)
# print r.content