一、需要安装的python库:
1.pybloom
2.redis
3.parsel
4.gevent
5.requests
6.chardet
7.MySQLdb

二、需要安装的数据库:
1.redis
2.mysql

三、实现的功能
1.用redis做url队列
2.http缓存
3.自动请求调优，尽可能保证每次请求的间隔都不一样
4.gevent并发请求

四、待完善
1.解析js网页，selenium+phantomjs
2.重用tcp/ip链接，urllib3
3.更新已下载的网页
4.登录验证
......

五、代码范例为抓取豆瓣电影
..........................
save.py
spider.py
my_redis.py
这三个脚本单独运行运行
