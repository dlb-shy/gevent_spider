#-*-coding:utf-8-*-
#!/usr/bin python
from gevent import monkey; monkey.patch_all()
import gevent
import logging
import logging.config
import random
import time
import json
import signal
import redis
import sys
import http_request
import my_settings
import myconnection

class HuSpider(myconnection.RedisConnect):
	"""

	生成初始url，进行抓取，然后调用http请求，生成response,之后解析网页，
	
	"""	
	logging.config.dictConfig(my_settings.my_logging_config)
	def __init__(self):
		"""
		"""
		super(HuSpider, self).__init__()
		self.my_request = http_request.HttpRequest()
		self.logger = logging.getLogger('HSpider')
		
	def start_request(self):
		"""

		根据给定的初始连接生成第一个response,这个方法只会运行一次
		"""
		self.logger.info('begin to crawl first url[%s]', my_settings.first_url)
		self.my_request.get(url=my_settings.first_url, base_url=None)
						
	def make_request(self):
		"""

		从redis服务器中的url_queue队列中取出url,进行抓取
		"""
		#网页并发请求次数
		num = my_settings.requests_count		
		url_list = []
		while 1:
			#将接受到ctrl+c信号时，就终止程序
			signal.signal(signal.SIGINT, self.close_spider)			
			if self.r.llen('url_queue'):#只要redis服务器中url_queue中有url,长度就不会为0
				#从redis服务器的url_queue中取出一个item,取出的是一个元组对，
				#第一个元素是队列的名字（即'url_queue'），第二个才是目标元素
				result = json.loads(self.r.blpop('url_queue', 0)[1])
					
				url_list.append((result['url'], result['base_url']))
					
				if len(url_list) == num or self.r.llen('url_queue') == 0:
					greenlets = [gevent.spawn(self.my_request.get, url, base_url) for url, base_url in url_list]
					gevent.joinall(greenlets)					
					url_list = []	
					
	def close_spider(self, signum, frame):
		"""
		捕获信号，关闭spider
		"""
		print u'程序将要停止运行'
		sys.exit(1)


if __name__  == "__main__":
	print 'start myspider!'
	myspider = HuSpider()
	
	if myspider.r.llen('url_queue') == 0:
		#如果redis服务器的url_queue队列为空，那么就请求初始url，否则直接从url_queue队列中取出url开始请求
		myspider.start_request()

	myspider.make_request()
	

	
