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
import signal
import MySQLdb
import my_settings
import myconnection
		
class Html_Handle(myconnection.MySQLConnect, myconnection.RedisConnect):
	logging.config.dictConfig(my_settings.my_logging_config)
	def __init__(self):
		#这里不用super()去继承父类的原因是在多重继承的情况下
		#super()只会查找一个父类		
		myconnection.MySQLConnect.__init__()
		myconnection.RedisConnect.__init__()

		self.patten = re.compile(r'/subject/[0-9]+/$')
		self.logger = logging.getLogger('HSpider')

	def parse_and_save_html(self):
		while 1:
			#signal.SIGINT信号对应的是ctrl+c,当收到这个信号时就调用stop函数
			signal.signal(signal.SIGINT, self.stop)
			if self.r.llen('html'):
				content = json.loads(self.r.brpop('html', 0)[1])
				item = my_settings.my_item#用于提取结构化数据
				if content['http_code'] == 200:
					sel = parsel.Selector(text=content['html'], type='html')
					#url的格式符合正则表达式，说明对应的response需要提取结构化数据
					if self.patten.search(content['url']):
						
						#提取结构化数据
						item['movie_name'] = sel.xpath('//h1/span[@property="v:itemreviewed"]/text()').extract()
						item['movie_year'] = sel.xpath('//span[@property="v:initialReleaseDate"]/text()').extract()
						item['movie_type'] = sel.xpath('//span[@property="v:genre"]/text()').extract()
						item['movie_rate'] = sel.xpath('//strong[@class="ll rating_num"]/text()').extract()
					else:
						#提取待抓取的未过滤的urls
						urls = sel.xpath('//a/@href').re(r'/subject/[0-9]+/$|/tag/.*')
						url_list = list(set(urls))
						#这里需要传输url的原因，是因为网页中提取出来的可能是相对网址，在后续操作中需要将相对网址补充为绝对网址
						result = json.dumps({'url': content['url'], 'url_list': url_list})
						self.r.rpush('unbloom_url_queue', result)
						
                #下面的sql语句没有写完整，需要补充完整
				self.cousor.execute('insert into douban () values ()',(content['url'], content['http_code'],
					                content['response_headers'], content['html'],item['movie_name'], item['movie_year'], 
					                item['movie_type'], item['movie_rate']))
				self.connect.commit()

	def stop(self, signum, frame):
		print u'程序将要停止运行......'
		self.cousor.close()
		self.connect.close()
		sys.exit(1)


if __name__ == '__main__':
	test = Html_Handle()
	test.parse_and_save_html()
