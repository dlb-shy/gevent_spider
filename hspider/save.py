
#-*-coding:utf-8-*-
#!/usr/bin python
import os
import json
import my_settings


def save_item_to_file(item):
	
	item['movie_name'] = (''.join(item['movie_name'])).encode('utf-8')
	item['movie_year'] = (''.join(item['movie_year'])).encode('utf-8')
	item['movie_type'] = ('-'.join(item['movie_type'])).encode('utf-8')
	item['movie_rate'] = (''.join(item['movie_rate'])).encode('utf-8')
	item['url' ] = item['url'].encode('utf-8')

	with open(my_settings.item_filename, 'a') as f:
		f.write('%s, %s, %s, %s, %s%s'%(item['movie_name'], item['movie_year'], item['movie_type'], item['movie_rate'],item['url'], os.linesep))


class Save(object):
	"""

	保存结构化数据到数据库
	"""

	def __init__(self, host, password):
		pass

		
	def save_item_to_sql(self, item):
		pass






