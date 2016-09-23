#-*-coding:utf-8-*-
#!/usr/bin python
"""
该脚本单独运行于redis服务器。用于将列表unbloom_url_queue的每一个元素作用于bloomfilter
然后生成新的url，并放到url_queue队列中
"""
from gevent import monkey;monkey.patch_all()
import redis
import json
import os
import sys; sys.path.append('/home/hujun/hspider')
import re
import urlparse
from pybloom import BloomFilter
import my_settings

class MyRedis(object):
	"""

	redis
	"""
	def __init__(self):
		"""
		xxx
		"""
		self.pool = redis.ConnectionPool(host=my_settings.host, port=my_settings.port, db=0)
		self.r = redis.StrictRedis(connection_pool=self.pool)
		
		try:
			f = open('/home/hujun/bloomfilter.txt')#尝试打开保存bloomfilter的文件
		except IOError:
			print 'create a new bloomfilter without file'
			#如果打开失败，说明不存在这个文件，就重新创建一个bloomfilter
			self.bloomfilter = BloomFilter(capacity=1000000, error_rate=0.00001)

			#初始化bloomfilter之后，直接将第一次抓取的url加到bloomfilter中
			self.bloomfilter.add(my_settings.first_url)
		else:
			print 'reload bloomfilter from a file'
			self.bloomfilter = BloomFilter.fromfile(f)

		self.patten = re.compile(r'((http[s]?)://(\w+\.)?\w+\.\w+)/?')#用于从url中提取出主域


	def bloom_filter_url(self):
		"""

		将unbloom_url_queue这个队列中的url过滤,取出未抓取的url到url_queue中
		"""
		print 'begin to filter url!'
		while 1:
			try:
				if self.r.llen('unbloom_url_queue'):#判断unbloom_url_queue的长度是否为0，如果为0，说明里面不存在元素
					item = self.r.brpop('unbloom_url_queue', 0)#从unbloom_url_queue中取出urls，阻塞版本
					url_list = item[1]
					url_list = json.loads(url_list)#将urls还原为元组的格式,为（url, urls）的元组格式
					urls = url_list[1]
					parse_url = urlparse.urlparse(url_list[0])
					domain = parse_url.scheme + '://' + parse_url.netloc#提取出协议加主机名，比如‘https://movie.douban.com’

					for url in urls:	
						if (domain not in url) and (parse_url[0] in url):#这一步就可以排除所有不在domain下的url,比如‘https://www.douban.com’这个域名以及该域名下的所有url就会被排除
							del url
						else:
							if domain not in url:#这一步判断url是否为完整的url
								url = domain + url
							if not self.bloomfilter.add(url):#判断url是否在bloomfilter中
								print url,'yes'
								self.r.rpush('url_queue', url)
			except KeyboardInterrupt:
			#捕获异常.当需要退出的时候就在键盘上按下ctrl+c，这时程序就会退出。捕获这个异常，并且保存bloomfilter到文件
				print u"""
				退出程序,请按0
				暂停程序,请按任何非0字符
				"""
				num = raw_input('>')
				if num == '0':
					with open('/home/hujun/bloomfilter.txt', 'w') as f:
						print 'save bloomfilter'
						self.bloomfilter.tofile(f)#将bloomfilter保存到文件
						self.r.save#同步保存redis数据到磁盘
						print u'ready to exit'
						sys.exit(1)
				else:
					print u"""
					程序已经处于暂停暂停
					重新启动，请按任何非0字符
					退出程序，请按0
					"""
					count = raw_input('>')
					if count == '0':
						with open('/home/hujun/bloomfilter.txt', 'w') as f:
							print 'save bloomfilter'
							self.bloomfilter.tofile(f)#将bloomfilter保存到文件
							print u'ready to exit'
							sys.exit(1)
					else:
						print u'程序重新开始运行'
						continue



if __name__ == "__main__":
	my_redis = MyRedis()
	my_redis.bloom_filter_url()
