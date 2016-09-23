#-*-coding:utf-8-*-
#!/usr/bin python
from gevent import monkey; monkey.patch_all()
import gevent
import logging
import logging.config
import random
import time
import json
import redis
import sys; sys.path.append('/home/hujun/hspider')
import http_request
import my_settings

#记录抓取的日志
logging.config.dictConfig(my_settings.my_logging_config)
logger = logging.getLogger('HSpider')

class HuSpider(object):
	"""

	生成初始url，进行抓取，然后调用http请求，生成response,之后解析网页，
	
	"""
	
	def __init__(self):
		#创建redis服务器的连接池
		self.pool = redis.ConnectionPool(host=my_settings.host, port=my_settings.port, db=0)
		self.r = redis.StrictRedis(connection_pool=self.pool)

		#实例化自定义的类
		self.my_request = http_request.Hu_httprequest()

		
	def start_request(self):
		"""

		根据给定的初始连接生成第一个response,这个方法只会运行一次
		"""
		logger.info('begin to crawl first url[%s]', my_settings.first_url)
		self.my_request.get(my_settings.first_url)

						
	def make_request(self):
		"""

		从redis服务器中的url_queue队列中取出url,进行抓取
		"""
		#生成随机并发请求次数，最多不超过settings.max_requests_count次数
		num = random.randint(my_settings.min_requests_count, my_settings.max_requests_count)
		
		url_list = []
		while 1:
			try:
				if self.r.llen('url_queue') != 0:#只要redis服务器中url_queue中有url,长度就不会为0
					#从redis服务器的url_queue中取出一个url,注意取出的是一个元组对，第一个元素是队列的名字，第二个才是目标元素
					result = self.r.blpop('url_queue', 0)
					url = result[1]
					url_list.append(url)

					if len(url_list) == num or self.r.llen('url_queue') == 0:
						#利用gevent进行请求
						threads = [gevent.spawn(self.my_request.get, url) for url in url_list]
						gevent.joinall(threads)
					
						url_list = []
						my_time = random.randint(my_settings.time_min_delay, my_settings.time_max_delay)#设置下载延迟
						print u'进入本次下载延迟，本次延迟[%d]秒!'%my_time
						time.sleep(my_time)
				else:
					print u'redis的url_queue队列为空,请稍等......'
				
			except KeyboardInterrupt:#捕获键盘上的ctrl+c
				print u"""
				退出程序,请按0
				暂停程序,请按任何非0字符
				"""
				num = raw_input('>')
				if num == '0':
					self.r.save
					sys.exit(1)
				else:
					print u"""
					程序已经处于暂停暂停
					重新启动，请按任何非0字符
					退出程序，请按0
					"""
					count = raw_input(">")
					if count == '0':
						sys.exit(1)
					else:
						print u'程序重新开始运行'
						continue

					
	def close_spider(self):
		"""

		设定一些抓取目标，达到目标了自动关闭spider
		"""
		pass


if __name__  == "__main__":
	print 'start myspider!'
	myspider = HuSpider()
	
	if myspider.r.llen('url_queue') == 0:
		#如果redis服务器的url_queue队列为空，那么就请求初始url，否则直接从url_queue队列中取出url开始请求
		myspider.start_request()

	myspider.make_request()
	

	
