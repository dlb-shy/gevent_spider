#-*-coding:utf-8-*-
#!/usr/bin python
import logging
import random
import time
import json
import redis
import sys
import gevent
from gevent import monkey; monkey.patch_all()
import http_request
import save 
import my_settings

sys.path.append(my_settings.path)

class HuSpider(object):
	"""

	生成初始url，进行抓取，然后调用http请求，生成response,之后解析网页，
	
	"""
	#记录抓取的日志
	logging.basicConfig(filename=my_settings.log_filename, level=logging.DEBUG, format=my_settings.log_format, datefmt='%Y/%m/%d %I:%M:%S %p')

	
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
		print 'begin first request'
		logging.info(u'开始抓取第一个url[%s]',my_settings.first_url)
		first_urls = self.my_request.get(my_settings.first_url)

		first_urls = json.dumps(first_urls)
		#将first_urls放到redis服务器中的unbloom_url_queue队列中
		self.r.rpush('unbloom_url_queue', first_urls)

					
	def make_request(self):
		"""

		从redis服务器中的url_queue队列中取出url,进行抓取
		"""
		print u'ready to make request'

		#生成随机并发请求次数，最多不超过settings.max_requests_count次数
		num = random.randint(my_settings.min_requests_count, my_settings.max_requests_count)
		
		url_list = []
		while 1:
			if self.r.llen('url_queue') != 0:#只要redis服务器中url_queue中有url,长度就不会为0
				#从redis服务器的url_queue中取出一个url,注意取出的是一个元组对，第一个元素是队列的名字，第二个才是目标元素
				result = self.r.blpop('url_queue', 0)
				url = result[1]
				
				logging.info('will begin to crawl url[%s]',url)
				url_list.append(url)

				if len(url_list) == num or self.r.llen('url_queue') == 0:
					#利用gevent进行请求
					threads = [gevent.spawn(self.my_request.get, url) for url in url_list]
					gevent.joinall(threads)
				
					url_list = []
					time.sleep(random.randint(my_settings.time_min_delay, my_settings.time_max_delay))#设置下载延迟
			
	
					
	def close_spider(self):
		"""

		设定一些抓取目标，达到目标了自动关闭spider
		"""
		pass


if __name__  == "__main__":
	print 'start myspider!'
	myspider = HuSpider()
	
	if myspider.r.llen('url_queue') == 0:#如果redis服务器的url_queue队列为空，那么就请求初始url，否则直接从url_queue队列中取出url开始请求
		myspider.start_request()

	myspider.make_request()
	

	
