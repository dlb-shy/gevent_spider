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
import requests; requests.adapters.DEFAULT_RETRIES = 5 
from chardet.universaldetector import UniversalDetector
from cStringIO import StringIO
import my_settings
import save
import myconnection

class HttpRequest(myconnection.RedisConnect):
	logging.config.dictConfig(my_settings.my_logging_config)
	def __init__(self):
		#redis连接
		super(HttpRequest, self).__init__()
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
		#执行数据库的缓存查找，如果可以找到网页就直接返回
		if self.findcache.find_cache(url):
			self.logger.info('[%s] has been download', url)
		else:
			#如果redis集合中的ip_set集合为空，就使用本机ip
			proxies = self.r.srandmember('ip_set') if self.r.scard('ip_set') else None
			#设置请求延迟
			self.throttle.request_delay(url)	
			try:
				host = urlparse.urlparse(url).netloc
				headers={'user-agent':random.choice(my_settings.user_agent),
						'accept-encoding':"gzip",
						'host':host,
						'accept':'text/html',
						'accept-charset':'utf-8',
						'accept-language':'zh-cn'}
				if base_url:
					headers['referer'] = base_url
				response = requests.get(url=url, 
						 				headers=headers,
										timeout=5, 
										allow_redirects=False,
										proxies=proxies,
										verify=True)
				self.logger.info('successfully download url [%s]', url)
			#捕获请求失败的url以及相应的错误,并写入redis的request_failed_queue队列
			except requests.exceptions.RequestException, e:
				#reason = '%s,%s'%(url, e)
				self.logger.error('failed to crawl url [%s],the reason is [%s]', url, e)
				#self.r.rpush('request_failed_queue', url)
			else:
				response.encoding = webpage_code(response)
				content = json.dumps({'url': url, 'http_code': response.status_code, 
				           'response_headers': unicode(dict(response.headers)), 'html': response.text})
				self.r.rpush('html', content)
												
	def get_js_webpage(self):
		"""

		解析js页面
		"""
		pass

	def get_sign_in_page(self):
		"""

		抓取需要登录的页面
		"""
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
	def __init__(self, time_delay=my_settings.time_delay):
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
		    	time.sleep(sleep_time * random.uniform(0.5, 1.25))
		#更新domain最后一次的访问时间
		self.domains[domain] = datetime.datetime.now()


class FindCache(myconnection.MySQLConnect):
	"""
	查找mysql数据库中的网页是否有缓存
	"""
	def __init__(self):
		super(FindCache, self).__init__()

	def find_cache(self, url):
		self.cousor.execute('select html from douban where url=%s',(url.encode('utf-8'),))
		self.connect.commit()
		html = self.cousor.fetchone()
		a = 1 if html else 0
		return a


def webpage_code(response):#解决网页编码问题
	"""

	解决网页的编码问题,获取网页的编码
	"""
	patten = re.compile(r'charset=(.+)[\"\']>')
	if patten.search(response.content) is not None:#使用正则表达式检测网页中是否存在charset
		
		charset = patten.search(response.content).group(1)
		return charset.strip('\' or \"').lower()

	else:#使用chardet去猜测编码
		
		my_stringio = StringIO(response.content)
		my_detector = UniversalDetector()
		for x in my_stringio:
			my_detector.feed(x)
			if my_detector.done:
				break
		my_detector.close()
		return my_detector.result['encoding']
