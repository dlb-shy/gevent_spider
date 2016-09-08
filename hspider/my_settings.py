
#-*-coding:utf-8-*-
#!/usr/bin python

"""

基本的设置
"""
#redis host port ，默认链接本地 
host = '127.0.0.1'
port = 6379

#spider所在的目录的path
path = '/home/hspider' #spider所在的目录，自行编辑

#保存item的文件名
item_filename = r'/home/item.txt' #存放item的文件，自行编辑

#保存ip的文件,用于给每个请求创建代理
ip_filename = r'/home/ip.txt' #自行编辑路径

#logging file
log_filename = r'/home//log.txt' #保存log的文件，自行编辑

#logging format
log_format = '%(asctime)s--%(levelname)s:%(message)s'



#默认的user-agent
#user_agent_filename = ''

#默认的请求头部
#headers = ''

#默认的最大抓取间隔
time_max_delay = 8

#smallest crawl delay
time_min_delay = 3

#单站点最大并发抓取
max_requests_count = 5

#first request url
first_url = r'https://movie.douban.com'

#需要抓取的站点的主域
domain = r'https://movie.douban.com'


#设置下载目标,比如保存的item数量
item_num = 500
