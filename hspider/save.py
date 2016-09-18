#-*-coding:utf-8-*-
#!/usr/bin python
import os
import json
import redis
import my_settings


def save_item_to_file():
	
	"""

	从redis的item_queue队列中获取item数据,并保存到本地文件
	"""
	pool = redis.ConnectionPool(host=my_settings.host, port=my_settings.port, db=0)
	r = redis.StrictRedis(connection_pool=pool)
	while 1:
		try:
			if r.llen('item_queue') != 0:
				print 'item to save!'
				result = r.brpop('item_queue',0)
				item = result[1]
				item =json.loads(item)
				item['movie_name'] = (''.join(item['movie_name'])).encode('utf-8')
				item['movie_year'] = (''.join(item['movie_year'])).encode('utf-8')
				item['movie_type'] = ('-'.join(item['movie_type'])).encode('utf-8')
				item['movie_rate'] = (''.join(item['movie_rate'])).encode('utf-8')
				item['url'] = item['url'].encode('utf-8')
	
				with open(my_settings.item_filename, 'a') as f:
					f.write('%s, %s, %s, %s, %s%s'%(item['movie_name'], item['movie_year'], item['movie_type'], item['movie_rate'],item['url'], os.linesep))
		except KeyboardInterrupt:#捕获键盘上的ctrl+c
			print u'''
			退出程序,请按0
			暂停程序,请按任何非0字符
			'''
			num = raw_input('>')
			if num == '0':
				r.save
				sys.exit(1)
			else:
				print u'''
				程序已经处于暂停状态
				重新启动，请按任何非0字符
				退出程序，请按0
				'''
				count = raw_input(">")
				if count == '0':
					r.save
					sys.exit(1)
				else:
					print u'程序重新开始运行'
					continue

class Save(object):
	"""

	保存结构化数据到数据库
	"""

	def __init__(self, host, password):
		pass

		
	def save_item_to_sql(self, item):
		pass



if __name__ == "__main__":
	save_item_to_file()

