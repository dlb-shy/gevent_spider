
#-*-coding:utf-8-*-
#!/usr/bin python
import requests
import re
import json
import redis
from scrapy.selector import Selector
import my_settings

class Hu_httprequest(object):

	def __init__(self):
		with open(my_settings.ip_filename,'r') as f:
			self.ip_list = f.readlines()
		self.patten = re.compile(r'/subject/[0-9]+/.*')
		self.headers = {'user-agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36'}

		#创建redis服务器的连接池
		self.pool = redis.ConnectionPool(host=my_settings.host, port=my_settings.port, db=0)
		self.r = redis.StrictRedis(connection_pool=self.pool)

		
	def get(self, url):
		"""

		用于请求静态的html链接,然后解析页面
		"""
		if self.ip_list == []:#默认不更换代理，使用本机ip
			try:
				response = requests.get(url, headers=self.headers, params=None, timeout=5, allow_redirects=True, cookies=None)
			except requests.exceptions.RequestException, e:#捕获请求失败的url以及相应的错误,并写入redis的request_failed_queue队列
				reason = '%s,%s'%(url, e)
				self.r.rpush('request_failed_queue', reason)
			else:
				sel = Selector(response=response, type='html')
				if self.patten.search(url):#如果该url的response符合需要提取item
					
					item = {'movie_name':1, 'movie_year':1, 'movie_type':1, 'movie_rate':1,'url':1}#在字典中定义一些字段，用于提取结构化数据

					#提取结构化数据
					item['movie_name'] = sel.xpath('//h1/span[@property="v:itemreviewed"]/text()').extract()
					item['movie_year'] = sel.xpath('//span[@property="v:initialReleaseDate"]/text()').extract()
					item['movie_type'] = sel.xpath('//span[@property="v:genre"]/text()').extract()
					item['movie_rate'] = sel.xpath('//strong[@class="ll rating_num"]/text()').extract()
					item['url'] = url
					
					return item
	
				else:
					#提取待抓取的未过滤的urls
					urls = sel.xpath('//a/@href').re(r'/subject/[0-9]+/.*|/tag/.*')
					urls = list(set(urls))

					return urls
								
		else:
			pass

	

	
