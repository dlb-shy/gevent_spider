需要安装的python库：
1.pybloom
2.redis
3.scrapy(主要是用到了srapy的Selector解析器)

需要安装的数据库:
redis

实现的功能：
1.待抓取url队列永久保存
2.用bloomfilter过滤url
3.一定程度上实现了分布式

待完善的功能：
1.url调度
2.解析js
3.抓取登录的网页
4......

代码执行顺序：
1.首先在终端执行my_redis.py
2.再在终端执行spider.py
