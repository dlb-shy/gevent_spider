#-*-coding:utf-8-*-
#!/usr/bin python
import requests
import re
import json
import redis
import chardet
import random
from scrapy.selector import Selector
import my_settings

class Hu_httprequest(object):

	def __init__(self):
		with open(my_settings.ip_filename,'r') as f:
			self.ip_list = f.readlines()
		self.patten = re.compile(r'/subject/[0-9]+/$')
		
		#创建redis服务器的连接池
		self.pool = redis.ConnectionPool(host=my_settings.host, port=my_settings.port, db=0)
		self.r = redis.StrictRedis(connection_pool=self.pool)

		
	def get(self, url):
		"""

		用于请求静态的html链接,然后解析页面
		"""
		if self.r.scard('ip_set') == 0:#如果redis集合中的ip_set集合为空，就使用本机ip
			try:
				response = requests.get(url, headers={'user-agent':random.choice(my_settings.user_agent)}, params=None, timeout=5, allow_redirects=True, cookies=None)
			except requests.exceptions.RequestException, e:#捕获请求失败的url以及相应的错误,并写入redis的request_failed_queue队列
				reason = '%s,%s'%(url, e)
				self.r.rpush('request_failed_queue', reason)
			else:
				#print response.encoding,1
				response.encoding = webpage_code(response)#使用正确的编码来解码网页
				#print response.encoding,2
				sel = Selector(text=response.text, type='html')
				if self.patten.search(url):#如果该url的response符合需要提取item
					print url
					item = {'movie_name':1, 'movie_year':1, 'movie_type':1, 'movie_rate':1,'url':1}#在字典中定义一些字段，用于提取结构化数据

					#提取结构化数据
					item['movie_name'] = sel.xpath('//h1/span[@property="v:itemreviewed"]/text()').extract()
					item['movie_year'] = sel.xpath('//span[@property="v:initialReleaseDate"]/text()').extract()
					item['movie_type'] = sel.xpath('//span[@property="v:genre"]/text()').extract()
					item['movie_rate'] = sel.xpath('//strong[@class="ll rating_num"]/text()').extract()
					item['url'] = url
					
					result = json.dumps(item)#统一以json的格式传输，从队列中取出的时候，在用json.loads()还原为原本格式
					self.r.rpush('item_queue', result)
	
				else:
					#提取待抓取的未过滤的urls
					urls = sel.xpath('//a/@href').re(r'/subject/[0-9]+/.*|/tag/.*')
					urls = list(set(urls))

					result = json.dumps((url, urls))#这里需要传输url的原因，是因为网页中提取出来的可能是相对网址，在后续操作中需要将相对网址补充为绝对网址
					self.r.rpush('unbloom_url_queue', result)
		else:
			pass


def webpage_code(response):#解决网页编码问题
	"""

	解决网页的编码问题,因为requests解码网页所使用的编码不一定是正确的编码类型
	"""
	sel = Selector(response=response, type='html')
	if sel.xpath('//meta').re(r'charset=[\"\'](.+)[\"\']') != []:
		charset = sel.xpath('//meta').re(r'charset=[\"\'](.+)[\"\']')#使用网页的charset内容，运用xpath和正则提取出编码
		return ''.join(charset).lower()#因为xpath返回的结果是单项列表,所以需要转换为字符串

	elif sel.xpath('//meta/@content').re('.*charset=(.+)') != []:
		charset = sel.xpath('//meta/@content').re('.*charset=(.+)')
		return ''.join(charset).lower()

	else:#使用chardet去猜测编码
		my_stringio = StringIO(response.content)
		my_detector = UniversalDetector()
		for x in my_stringio:
			my_detector.feed(x)
			if my_detector.done:
				break
		my_detector.close()
		return my_detector.result['encoding']

	
	

	
