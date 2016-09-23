#-*-coding:utf-8-*-
#!/usr/bin python
from gevent import monkey;monkey.patch_all()
import os
import json
import sys
import logging
import logging.config
import redis
import my_settings

logging.config.dictConfig(my_settings.my_logging_config)
logger = logging.getLogger('HSpider')

class Save(object):

	logging.config.dictConfig(my_settings.my_logging_config)
	logger = logging.getLogger('HSpider')

	def __init__(self):
		self.pool = redis.ConnectionPool(host=my_settings.host, port=my_settings.port, db=0)
		self.r = redis.StrictRedis(connection_pool=self.pool)

		
	def save_to_file(self):
		"""

		从redis列表中的response_queue中获取response对象，然后进行相关处理
		"""
		while 1:
			try:
				if self.r.llen('item_queue'):#判断该队列是否为空
					print u'save_item'
					result = self.r.brpop('item_queue', 0)[1]
					item = json.loads(result)
					print item
					item['movie_name'] = (''.join(item['movie_name'])).encode('utf-8')
					item['movie_year'] = (''.join(item['movie_year'])).encode('utf-8')
					item['movie_type'] = ('-'.join(item['movie_type'])).encode('utf-8')
					item['movie_rate'] = (''.join(item['movie_rate'])).encode('utf-8')
					item['url' ] = item['url'].encode('utf-8')

					with open(my_settings.item_filename, 'a') as f:
						f.write('%s, %s, %s, %s, %s%s'%(item['movie_name'], 
							item['movie_year'], 
							item['movie_type'], 
							item['movie_rate'],
							item['url'],
							 os.linesep))
						logger.info('successfully to save item [%s]', item['movie_name'])
			except KeyboardInterrupt:#捕获键盘上的ctrl+c
				print u'''
				退出程序,请按0
				暂停程序,请按任何非0字符
				'''
				num = raw_input('>')
				if num == '0':
					self.r.save
					sys.exit(1)
				else:
					print u'''
					程序已经处于暂停状态
					重新启动，请按任何非0字符
					退出程序，请按0
					'''
					count = raw_input(">")
					if count == '0':
						sys.exit(1)
					else:
						print u'程序重新开始运行'
						continue




if __name__ == '__main__':
	test = Save()
	test.save_to_file()
