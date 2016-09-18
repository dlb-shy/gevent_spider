需要安装的python库:
1.pybloom
2.redis
3.scrapy(用到了srapy的Selector解析器)
4.gevent
5.requests

需要安装的数据库:
redis

实现的功能:
1.待抓取url队列永久保存
2.用bloomfilter过滤url
3.共享一个url队列，实现了分布式
4.检测网页编码
5.暂停,继续,终止程序

待完善:
1.可以改用urllib3,使用其中的连接池,这样就可以重用底层的tcp/ip链接,减少request的消耗
2.不能解析js网页,正在完善中,使用splash
3.暂时没有登录功能,没有记录cookie
4.......


代码范例为抓取豆瓣电影

..........................
save.py
spider.py
my_redis.py
这三个程序需要打开三个终端分别运行
