#-*-coding:utf-8-*-
#!/usr/bin python
from gevent import monkey;monkey.patch_all()
import requests
import re
import json
import redis
import random
import urllib3
from parsel import Selector
from chardet.universaldetector import UniversalDetector
from cStringIO import StringIO
import my_settings

class Hu_httprequest(object):

	def __init__(self):
		
		#创建redis服务器的连接池
		self.pool = redis.ConnectionPool(host=my_settings.host, port=my_settings.port, db=0)
		self.r = redis.StrictRedis(connection_pool=self.pool)

		#使用urllib3,创建http连接池,重用底层的tcp/ip链接,如果连接的是https的站点,需要设置证书
		self.http = urllib3.PoolManager(maxsize=10, num_pools=5)

		self.patten = re.compile(r'/subject/[0-9]+/$')

	def get(self, url):
		"""

		用于请求静态的html链接,然后解析页面
		"""
		if self.r.scard('ip_set') == 0:#如果redis集合中的ip_set集合为空，就使用本机ip
			try:
				response = self.http.request(method='GET',
				 							url=url, 
				 							headers={'user-agent':random.choice(my_settings.user_agent),
													'accept-encoding':"gzip, deflate, sdch",
													'connection':'keep-alive'},#使得response是启用了gzip压缩的, 
											timeout=5, 
											redirect=False, 
											reties=False)
			except urllib3.exceptions.HTTPError, e:#捕获请求失败的url以及相应的错误,并写入redis的request_failed_queue队列
				reason = '%s,%s'%(url, e)
				self.r.rpush('request_failed_queue', reason)
			else:
				page_coding = webpage_code(response)
				sel = Selector(text=response.data.decode(page_coding), type='html')
				if self.patten.search(url):#url的格式符合正则表达式，说明对应的response需要提取结构化数据
					item = {'movie_name':1, 'movie_year':1, 'movie_type':1, 'movie_rate':1,'url':1}#在字典中定义一些字段，用于提取结构化数据

					#提取结构化数据
					item['movie_name'] = sel.xpath('//h1/span[@property="v:itemreviewed"]/text()').extract()
					item['movie_year'] = sel.xpath('//span[@property="v:initialReleaseDate"]/text()').extract()
					item['movie_type'] = sel.xpath('//span[@property="v:genre"]/text()').extract()
					item['movie_rate'] = sel.xpath('//strong[@class="ll rating_num"]/text()').extract()
					item['url'] = url

					result = json.dumps(item)
					self.r.rpush('item_queue', result)

				else:
					#提取待抓取的未过滤的urls
					urls = sel.xpath('//a/@href').re(r'/subject/[0-9]+/$|/tag/.*')
					urls = list(set(urls))
					result = json.dumps((url, urls))#这里需要传输url的原因，是因为网页中提取出来的可能是相对网址，在后续操作中需要将相对网址补充为绝对网址
					self.r.rpush('unbloom_url_queue', result)
								
		else:
			pass



	
	

	def get_js_webpage(self):
		pass


	def get_sign_in_page(self):
		pass


def webpage_code(response):#解决网页编码问题
	"""

	解决网页的编码问题,获取网页的编码
	"""
	patten = re.compile(r'<.*charset=(.+).*>')
	if patten.search(response.data).group(1):#使用正则表达式检测网页中是否存在charset
		
		charset = patten.search(response.data).group(1)
		return charset.strip('\' or \"').lower()

	else:#使用chardet去猜测编码
		
		my_stringio = StringIO(response.data)
		my_detector = UniversalDetector()
		for x in my_stringio:
			my_detector.feed(x)
			if my_detector.done:
				break
		my_detector.close()
		return my_detector.result['encoding']
