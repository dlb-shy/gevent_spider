#-*-coding:utf-8-*-
#!/usr/bin python
from gevent import monkey;monkey.patch_all()
import os
import json
import sys
import parsel
import logging
import logging.config
import redis
import re
import zlib
import signal
import config
import connects
import extract
import items
reload(sys)
sys.setdefaultencoding('utf-8')
		
class Html_Handle(object):
	def __init__(self):		
		self.db = connects.MySQL()
		self.redis = connects.RedisConnect(**config.redis_config)

		self.patten = re.compile(r'/subject/[0-9]+/$')
		self.logger = logging.getLogger('HSpider')

	def parse_and_save_html(self):
		while 1:
			#signal.SIGINT信号对应的是ctrl+c,当收到这个信号时就调用stop函数
			signal.signal(signal.SIGINT, self.stop)
			if self.redis.lindex('html'):
				content = self.redis.brpop('html')
				text = content['html'].decode('utf-8')
				extracts = extract.Extract(item=items.Item(), text=text, selector=parsel.Selector)
				#url的格式符合正则表达式，说明对应的response需要提取结构化数据
				if self.patten.search(content['url'].decode('utf-8')):	
					extracts.item_xpath('movie_name', '//h1/span[@property="v:itemreviewed"]/text()')
					extracts.item_xpath('movie_year', '//span[@property="v:initialReleaseDate"]/text()')
					extracts.item_xpath('movie_type', '//span[@property="v:genre"]/text()')
					extracts.item_xpath('movie_rate', '//strong[@class="ll rating_num"]/text()')
					item = extracts.get_item()
					result_item = (content['url'], 
							   item['movie_name'],
							   item['movie_year'],
							   item['movie_type'],
							   item['movie_rate'],)

					cmd = """insert into item (url, movie_name, movie_year,movie_type, movie_rate) 
						  values (%s, %s, %s, %s, %s)"""
					self.db.query(cmd, result_item)
				else:
					extracts.link_xpath('//a/@href', r'/subject/[0-9]+/$|/tag/.*')
					url_list = extracts.get_links()
					#这里需要传输url的原因，是因为网页中提取出来的可能是相对网址
					#在后续操作中需要将相对网址补充为绝对网址
					result = json.dumps({'url': content['url'], 'url_list': url_list})
					self.redis.rpush('unbloom_url_queue', result)

				html = zlib.compress(content['html'])
				headers = json.dumps(content['response_headers']).encode('utf-8')

				result1 = (content['url'], content['http_code'], headers, html,)
				cmd = """insert into html (url, http_code, response_headers, html) 
					  values (%s, %s, %s, %s)"""
				self.db.query(cmd, result1)
				self.logger.info('Save [%s] to MySQL', content['url'].encode('utf-8'))

	def stop(self, signum, frame):
		print u'程序将要停止运行......'
		sys.exit(1)

