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
import re
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

		self.patten = re.compile(r'((http[s]?)://(\w+\.)?\w+\.\w+)/?')#用于从url中提取出主域


	def bloom_filter_url(self):
		"""

		将unbloom_url_queue这个队列中的url过滤,取出未抓取的url到url_queue中
		"""
		print 'begin to filter url!'
		while 1:
			try:
				if self.r.llen('unbloom_url_queue') != 0:#判断unbloom_url_queue的长度是否为0，如果为0，说明里面不存在元素
					item = self.r.brpop('unbloom_url_queue', 0)#从unbloom_url_queue中取出urls，阻塞版本
					url_list = item[1]
					url_list = json.loads(url_list)#将urls还原为元组的格式,为（url, urls）的元组格式
					urls = url_list[1]
					domain = self.patten.search(url_list[0]).group(1)#提取主域名，比如r'https://movie.douban.com'。主要用于在抓取多个域名的时候，抓取单域名可以不需要
					#print domain
					if domain not in my_settings.domain:#判断提取出的domain是否在my_settings.domain中，如果不在就丢弃urls
						del urls
						continue
					else:
						prot_sch = self.patten.search(url_list[0]).group(2)#提取协议字段，要么是http，要么是https
						#print prot_sch
						for url in urls:
							if (domain not in url) and (prot_sch not in url):#判断该url是否在抓取的主域之下(即该url是否要继续抓取)且url是否为完整的url
								url = domain + url
								if not self.bloomfilter.add(url):#判断url是否在bloomfilter中
									print url,'yes'
									self.r.rpush('url_queue', url)
			except KeyboardInterrupt:
			#捕获异常.当需要退出的时候就在键盘上按下ctrl+c，这时程序就会退出。捕获这个异常，并且保存bloomfilter到文件
				with open('/home/hujun/bloomfilter.txt', 'w') as f:
					print 'save bloomfilter'
					self.bloomfilter.tofile(f)#将bloomfilter保存到文件
					self.r.save#同步保存redis数据到磁盘
					sys.exit(1)



if __name__ == "__main__":
	my_redis = MyRedis()
	my_redis.bloom_filter_url()
