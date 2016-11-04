#-*-coding:utf-8-*-
#!/usr/bin python
"""
该脚本单独运行于redis服务器。用于将列表unbloom_url_queue的每一个元素作用于bloomfilter
然后生成新的url，并放到url_queue队列中
"""
from gevent import monkey; monkey.patch_all()
import redis
import json
import os
import sys
import re
import signal
import urlparse
import urllib
from pybloom import BloomFilter
import config
import connects
reload(sys)
sys.setdefaultencoding('utf-8')

class MyRedis(object):
	"""
	redis
	"""
	def __init__(self):
		self.redis = connects.RedisConnect(**config.redis_config)
		#self.p = self.redis.r.pipeline()
		try:
			print u'正在初始化,请稍后.....'
			f = open('/home/hujun/bloomfilter.txt')#尝试打开保存bloomfilter的文件
		except IOError:
			print 'create a new bloomfilter without file'
			#如果打开失败，说明不存在这个文件，就重新创建一个bloomfilter
			self.bloomfilter = BloomFilter(capacity=1000000, error_rate=0.00001)
			#初始化bloomfilter之后，直接将第一次抓取的url加到bloomfilter中
			self.bloomfilter.add(config.first_url)
		else:
			print 'reload bloomfilter from a file'
			self.bloomfilter = BloomFilter.fromfile(f)

	def bloom_filter_url(self):
		"""
		将unbloom_url_queue这个队列中的url过滤,取出未抓取的url到url_queue中
		"""
		print 'begin to filter url!'
		while 1:
			#捕获信号ctrl+c,用于终止程序
			signal.signal(signal.SIGINT, self.stop)			
			if self.redis.lindex('unbloom_url_queue'):
				item = self.redis.brpop('unbloom_url_queue')
				url_list = item['url_list']
				base_url = item['url']
				parse_url = urlparse.urlparse(base_url)
				#提取domain，比如‘https://movie.douban.com’
				domain = '://'.join((parse_url.scheme, parse_url.netloc))
				for url in url_list:					
					#这一步就可以排除所有不在domain下的url,
					#比如‘https://www.douban.com’这个域名以及该域名下的所有url就会被排除
					if (parse_url.netloc not in url) and (parse_url.scheme in url):
						pass
					else:
						#这一步判断url是否为完整的url
						if domain not in url:
							url = ''.join([domain, url])
						if '#' in url:
							#如果url中存在#号，就删除它
							url = urlparse.urldefrag(url)[0]
						if len(url) >= 85:
							continue
						#url中可能存在转义字符,统一转化为原始字符,比如将%7e转化为~
						url = urllib.unquote(url)
						if not self.bloomfilter.add(url):#判断url是否在bloomfilter中
							print url
							new_item = json.dumps({'url': url, 
												   'base_url': base_url})				
							self.redis.rpush('url_queue', new_item)
				#else:
					#self.p.execute()
					
		
	def stop(self, signum, frame):
		print u'程序将要终止运行，正在保存bloomfilter到文件，请稍候......'
		with open('/home/hujun/bloomfilter.txt', 'w') as f:	
			self.bloomfilter.tofile(f)#将bloomfilter保存到文件
			print u'保存数据完成，即将退出'
			sys.exit(1)


if __name__ == "__main__":
	my_redis = MyRedis()
	my_redis.bloom_filter_url()