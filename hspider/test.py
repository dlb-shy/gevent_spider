#-*-coding:utf-8-*-
#!/usr/bin python

import os
import spider
import save

pid = os.fork()

if pid == 0:
	test = save.Html_Handle()
	test.parse_and_save_html()
else:
	myspider = spider.HuSpider()
	
	if not myspider.r.llen('url_queue'):#计算长度影响性能，需要改掉
		#如果redis服务器的url_queue队列为空，那么就请求初始url，
		#否则直接从url_queue队列中取出url开始请求
		myspider.start_request()

	myspider.make_request()
	