需要安装的python库：
1.pybloom
2.redis
3.scrapy(用到了srapy的Selector解析器)
4.gevent

需要安装的数据库:
redis

实现的功能：
1.待抓取url队列永久保存
2.用bloomfilter过滤url
3.共享一个url队列，实现了分布式

待完善的功能：
1.url调度
2.解析js
3.抓取登录的网页
4......


范例为抓取豆瓣电影
