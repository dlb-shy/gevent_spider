#-*-coding:utf-8-*-
#!/usr/bin python
from gevent import monkey; monkey.patch_all()
import requests
import urlparse
import re
import json
import redis
import logging
import logging.config
import random
import datetime
import time
from selenium import webdriver
import requests; requests.adapters.DEFAULT_RETRIES = 3
from chardet.universaldetector import UniversalDetector
from cStringIO import StringIO
import config
import save
import connects

class HttpRequest(object):
	
	def __init__(self):
		
		self.redis = connects.RedisConnect(**config.redis_config)
		self.throttle = Throttle()
		self.findcache = FindCache()
		self.logger = logging.getLogger('HSpider')

	def get(self, url, base_url):
		"""

		用于请求静态的html链接,然后解析页面
		参数:
			url:待抓取的url, str或者unicode
			base_url:待抓取url来源页面的url,主要用作构造headers中的referer
		"""
		#执行数据库的缓存查找，如果可以找到网页,就直接返回
		if self.findcache.find_cache(url):
			self.logger.info('[%s] has been cached', url)
		else:
			#如果redis集合中的ip_set集合为空，就使用本机ip
			#proxies = self.r.srandmember('ip_set') if self.r.scard('ip_set') else None
			#设置请求延迟
			self.throttle.request_delay(url)
			host = urlparse.urlparse(url).netloc
			headers={'user-agent':random.choice(config.user_agent),
					'accept-encoding':"gzip, deflate",
					'host':host,
					'accept':'text/html',
					'accept-charset':'utf-8',
					'accept-language':'zh-cn, zh;q=0.8'}

			if base_url:
				headers['referer'] = base_url

			try:
				response = requests.get(url=url, 
						 				headers=headers,
										timeout=5, 
										allow_redirects=False,
										verify=True)

			#捕获请求失败的url以及相应的错误,并写入redis的request_failed_queue队列
			except requests.exceptions.RequestException, e:
				self.logger.error('Failed [%s],Reason [%s]', url, e)
				#self.r.rpush('request_failed_queue', url)

			else:
				if self.pre_response(response, url, base_url):
					response.encoding = webpage_code(response)
					content = json.dumps({'url': url.encode('utf-8'), 
						                 'http_code': response.status_code, 
					                     'response_headers': dict(response.headers),
					                     'html': response.text.encode('utf-8')},)
					self.redis.rpush('html', item=content)

	def pre_response(self, response, url, base_url):
		"""
		预处理响应,过滤出响应状态码为200的response
		"""
		http_code = response.status_code
		if http_code == 200:
			self.logger.info('GET [%d] [%s]', http_code, url)
			return response

		elif 300 <= http_code <400:
			self.logger.warning('GET [%d] [%s]', http_code, url)
			new_url = response.headers['location']
			url_list = json.dumps({'url': new_url, 'base_url': base_url})
			self.redis.rpush('url_queue', item=url_list)

		elif 400 <= http_code <500:
			self.logger.error('GET [%d] [%s]', http_code, url)
			
		elif http_code >= 500:
			self.logger.critical('GET [%d] [%s]', http_code, url)
			url_list = json.dumps({'url': url, 'base_url': base_url})
			self.redis.rpush('url_queue', item=url_list)
		else:
			pass
												
		
class Throttle(object):
	"""
	用于请求调优
	self.domains中会记录每一个不同host最后一次访问的时间
	在每次请求url的时候，就提取出这个url的host,然后用当前
	时间减去self.domains中记录的时间，用产生的差值与self.time_delay
	进行比较即可得出一个需要睡眠的时间。最后我们在乘以一个系数
	就尽可能的可以保证每次请求的延迟都不一样
	"""
	def __init__(self, time_delay=config.time_delay):
		#用于记录每个域名最后的访问时间
		self.domains = {}
		self.time_delay = time_delay

	def request_delay(self, url):
		domain = urlparse.urlparse(url).netloc

		#获取domain最后的请求时间
		last_request_time = self.domains.get(domain)
		if last_request_time and self.time_delay > 0:
		    sleep_time = self.time_delay - (datetime.datetime.now() - last_request_time).seconds
		    if sleep_time > 0:
		    	time.sleep(sleep_time * random.uniform(0.5, 1))
		#更新domain最后一次的访问时间
		self.domains[domain] = datetime.datetime.now()


class FindCache(object):
	"""
	查找mysql数据库中的网页是否有缓存

	"""
	def __init__(self):
		self.db = connects.MySQL()

	def find_cache(self, url):
		cmd = u'select url from html where url=%s'
		item = (url.encode('utf-8'),)
		time.sleep(5)
		result = self.db.select(cmd, item)
		return result


class Driver(object):
	#抓取js页面
	#使用类来定义就可以使用同一个浏览器同一个窗口打开页面
	#这就可以保持会话状态，如果是登录的，一直持续登录
	#如果要同时打开两个窗口，只需要创建两个实例就可以
	def __init__(self, mydriver=u'chrome'):
		if mydriver == u'chrome':
		    self.driver = webdriver.Chrome(ur'd:\chrome\chromedriver.exe')
		elif mydriver == u'phantomjs':
		    self.driver = webdriver.PhantomJS(ur'd:\phantomjs\phantomjs\bin\phantomjs.exe')
		elif mydriver == u'firefox':
			#selenium对firefox的版本有要求，但是好像最新版的selenium没这个限制
		    self.driver = webdriver.Firefox()

	def get_signin(self, url):
		self.driver.get(url)
		try:
		#表示会至多等待10秒，如果定位的元素没找到就抛出TimeoutException
		    wait = WebDriverWait(self.driver, 10)
		    wait.until(EC.presence_of_element_located((By.XPATH, u'//input[@name="account"]')))
		except exceptions.TimeoutException as e:
		    pass
		else:
		    account = self.driver.find_element_by_xpath(u'//input[@name="account"]')
		    account.send_keys(u'524964426@qq.com')

		    password = self.driver.find_element_by_xpath(u'//input[@name="password"]')
		    password.send_keys(u'lymlhhj123')
			
		    remember_me = self.driver.find_element_by_xpath(u'//input[@name="remember_me"]')
		    remember_me.click()

		    submit = self.driver.find_element_by_xpath(u'//button[@class="sign-button submit"]')	
		    submit.click()
		finally:	
		    time.sleep(2)

	@property
	def cookies(self):
		return self.driver.get_cookies()

	def close(self):
		self.driver.close()


class SIGNIN(object):
	_HEADERS = {'user-agent': """Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 
		                        (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36""",
	           'accept': """text/html, application/xhtml+xml, 
	                        application/xml;q=0.9, image/webp,*/*;q=0.8""",
	           'accept-encoding': 'gzip, deflate',	           
	           'Accept-Language': 'zh-CN, zh;q=0.8',
	           'Cache-Control': 'no-cache',
	           'Connection': 'keep-alive',}
	def __init__(self, url):
		self.s = requests.Session()
		
	def sign_in(self, url):
		driver = Driver()
		driver.get_signin(url)
		raw_cookies = driver.cookies
		driver.close()
		cookies = {item['name']:item['value'] for item in raw_cookies}
		host = urlparse.urlparse(url).netloc
		SIGNIN._HEADERS['host'] = host
		self.s.get(url, headers=SIGNIN._HEADERS, cookies=cookies)

	def get(self, url):
		self.s.get(url)


def webpage_code(response):#解决网页编码问题
	"""

	解决网页的编码问题,获取网页的编码
	"""
	patten = re.compile(r'charset=(.+)[\"\']>')
	if patten.search(response.content) is not None:#使用正则表达式检测网页中是否存在charset
		
		charset = patten.search(response.content).group(1)
		return charset.strip('\'' or '\"').lower()

	else:#使用chardet去猜测编码
		
		my_stringio = StringIO(response.content)
		my_detector = UniversalDetector()
		for x in my_stringio:
			my_detector.feed(x)
			if my_detector.done:
				break
		my_detector.close()
		return my_detector.result['encoding']