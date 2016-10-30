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
import MySQLdb
import my_settings
import myconnection
import extract
reload(sys)
sys.setdefaultencoding('utf-8')
		
class Html_Handle(myconnection.MySQLConnect, myconnection.RedisConnect):
	logging.config.dictConfig(my_settings.my_logging_config)
	def __init__(self):
		#这里不用super()去继承父类的原因是在多重继承的情况下
		#super()只会查找一个父类		
		myconnection.MySQLConnect.__init__(self)
		myconnection.RedisConnect.__init__(self)

		self.patten = re.compile(r'/subject/[0-9]+/$')
		self.logger = logging.getLogger('HSpider')

	def parse_and_save_html(self):
		while 1:
			#signal.SIGINT信号对应的是ctrl+c,当收到这个信号时就调用stop函数
			signal.signal(signal.SIGINT, self.stop)
			if self.r.lindex('html', 0):
				content = json.loads(self.r.brpop('html', 0)[1])
				#item = my_settings.my_item#用于提取结构化数据
				text = content['html'].decode('utf-8')
				extracts = extract.Extract(text=text, selector=parsel.Selector)
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

					self.cousor.execute("""insert into item 
						            (url, movie_name, movie_year,movie_type, movie_rate) 
						            values (%s, %s, %s, %s, %s)""", result_item)
				else:
					extracts.link_xpath('//a/@href', r'/subject/[0-9]+/$|/tag/.*')
					url_list = extracts.get_links()
					#这里需要传输url的原因，是因为网页中提取出来的可能是相对网址
					#在后续操作中需要将相对网址补充为绝对网址
					result = json.dumps({'url': content['url'], 'url_list': url_list})
					self.r.rpush('unbloom_url_queue', result)

				html = zlib.compress(content['html'])
				headers = json.dumps(content['response_headers']).encode('utf-8')

				result1 = (content['url'],
				          content['http_code'],
				          headers, 
					      html,)

				self.cousor.execute("""insert into html 
					                   (url, http_code, response_headers, html) 
					                   values (%s, %s, %s, %s)""",result1)
				self.connect.commit()
				self.logger.info('Save [%s] to MySQL', content['url'].encode('utf-8'))

	def stop(self, signum, frame):
		print u'程序将要停止运行......'
		self.cousor.close()
		self.connect.close()
		sys.exit(1)

