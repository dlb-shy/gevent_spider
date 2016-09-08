
#-*-coding:utf-8-*-
#!/usr/bin python
"""
该脚本单独运行于redis服务器。用于将列表unbloom_url_queue的每一个元素作用于bloomfilter
然后生成新的url，并放到url_queue队列中
"""
import redis
import json
import os
import sys
from pybloom import BloomFilter
import my_settings

sys.path.append(my_settings.path)

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


	def bloom_filter_url(self):
		"""

		将unbloom_url_queue这个队列中的url过滤,取出未抓取的url到url_queue中
		"""
		print 'begin to filter url!'
		while 1:
			try:
				if self.r.llen('unbloom_url_queue') != 0:#判断unbloom_url_queue的长度是否为0，如果为0，说明里面不存在元素
					urls = self.r.brpop('unbloom_url_queue', 0)#从unbloom_url_queue中取出urls，阻塞版本
					urls = urls[1]
					urls = json.loads(urls)#将urls还原为列表的格式
					for url in urls:
						if my_settings.domain not in url:#判断url是否为完整的url
							url = my_settings.domain + url
						if not self.bloomfilter.add(url):#判断url是否在bloomfilter中
							print url,'yes'
							self.r.rpush('url_queue', url)
			except KeyboardInterrupt:
			#捕获异常.当需要退出的时候就在键盘上按下ctrl+c，这时程序就会退出。捕获这个异常，并且保存bloomfilter到文件
				with open('/home/hujun/bloomfilter.txt', 'w') as f:
					print 'save bloomfiltr'
					self.bloomfilter.tofile(f)
					sys.exit(1)



if __name__ == "__main__":
	my_redis = MyRedis()
	my_redis.bloom_filter_url()
