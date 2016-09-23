#-*-coding:utf-8-*-
#!/usr/bin python

"""

设置
"""
#redis host port ，默认链接本地 
host = '127.0.0.1'

port = 6379

#保存item的文件名
item_filename = r'/home/hujun/item.txt' #存放item的文件，自行编辑

#logging config
my_logging_config = {
					'version':1,
					'disable_existing_loggers':True,
					'formatters':{
						'filefmt':{
							'format':'%(asctime)s-%(name)s-%(levelname)s:%(message)s',
							'datefmt':'%Y-%m-%d %H:%M:%S'
								},
						'consolefmt':{
							'format':'%(asctime)s-%(name)s-%(levelname)s:%(message)s',
							'datafmt':'%Y-%m-%d %H:%M:%S'
						}
									},
					'handlers':{
						'filehandler':{
							'class':'logging.FileHandler',
							'level':'INFO',
							'formatter':'filefmt',
							'filename':r'/home/hujun/log.log',
							'encoding':'utf-8'
								},

						'consolehandler':{
							'class':'logging.StreamHandler',
							'level':'INFO',
							'formatter':'consolefmt',
							'stream':'ext://sys.stdout'
											}
									},
					'loggers':{
						'HSpider':{
							'level':'INFO',
							'handlers':['filehandler', 'consolehandler']
									}
								}
					
					}

#定义提取的结构化数据
my_item = {
	'movie_name':None,
	'movie_year':None, 
	'movie_type':None, 
	'movie_rate':None,
	'url':None}


#user-agent
user_agent = [
	"Mozilla/5.0+(Windows+NT+6.2;+WOW64)+AppleWebKit/537.36+(KHTML,+like+Gecko)+Chrome/45.0.2454.101+Safari/537.36",
	"Mozilla/5.0+(Windows+NT+5.1)+AppleWebKit/537.36+(KHTML,+like+Gecko)+Chrome/28.0.1500.95+Safari/537.36+SE+2.X+MetaSr+1.0",
	"Mozilla/5.0+(Windows+NT+6.1;+WOW64)+AppleWebKit/537.36+(KHTML,+like+Gecko)+Chrome/50.0.2657.3+Safari/537.36",
	"Mozilla/5.0+(Windows+NT+6.1;+WOW64)+AppleWebKit/537.36+(KHTML,+like+Gecko)+Chrome/51.0.2704.106+Safari/537.36",
	"Mozilla/5.0+(Windows+NT+6.1)+AppleWebKit/537.36+(KHTML,+like+Gecko)+Chrome/47.0.2526.108+Safari/537.36+2345Explorer/7.1.0.12633",
	"Mozilla/5.0+(Macintosh;+Intel+Mac+OS+X+10_11_4)+AppleWebKit/537.36+(KHTML,+like+Gecko)+Chrome/49.0.2623.110+Safari/537.36",
	"Mozilla/5.0+(Macintosh;+Intel+Mac+OS+X+10_9_5)+AppleWebKit/537.36+(KHTML,+like+Gecko)+Chrome/42.0.2311.152+Safari/537.36",
	"Mozilla/5.0+(Windows+NT+6.1;+WOW64)+AppleWebKit/537.36+(KHTML,+like+Gecko)+Chrome/42.0.2311.152+Safari/537.36",
	"Mozilla/5.0+(Macintosh;+Intel+Mac+OS+X+10_10_2)+AppleWebKit/600.3.18+(KHTML,+like+Gecko)+Version/8.0.3+Safari/600.3.18",
	"Mozilla/5.0+(Windows+NT+6.1;+WOW64)+AppleWebKit/537.36+(KHTML,+like+Gecko)+Chrome/49.0.2623.22+Safari/537.36+SE+2.X+MetaSr+1.0",
	"Mozilla/5.0+(Macintosh;+Intel+Mac+OS+X+10_11_4)+AppleWebKit/601.5.17+(KHTML,+like+Gecko)+Version/9.1+Safari/601.5.17",
	"Mozilla/5.0+(Windows+NT+6.1;+WOW64)+AppleWebKit/537.36+(KHTML,+like+Gecko)+Chrome/48.0.2564.103+Safari/537.36",
	"Mozilla/5.0+(Windows+NT+6.1;+WOW64)+AppleWebKit/537.36+(KHTML,+like+Gecko)+Chrome/47.0.2526.80+Safari/537.36+Core/1.47.640.400+QQBrowser/9.4.8309.400",
	"Mozilla/5.0+(Macintosh;+Intel+Mac+OS+X+10_10_5)+AppleWebKit/600.8.9+(KHTML,+like+Gecko)+Version/8.0.8+Safari/600.8.9",
	"Mozilla/5.0+(Windows+NT+6.3;+WOW64)+AppleWebKit/537.36+(KHTML,+like+Gecko)+Chrome/39.0.2171.99+Safari/537.36+2345Explorer/6.4.0.10356",
	"Mozilla/5.0+(Windows+NT+6.1;+WOW64)+AppleWebKit/537.36+(KHTML,+like+Gecko)+Chrome/45.0.2454.87+Safari/537.36+QQBrowser/9.2.5584.400",
	"Mozilla/5.0+(Windows+NT+6.1;+WOW64)+AppleWebKit/537.36+(KHTML,+like+Gecko)+Chrome/47.0.2526.111+Safari/537.36",
	"Mozilla/5.0+(Windows+NT+6.1;+WOW64)+AppleWebKit/537.36+(KHTML,+like+Gecko)+Chrome/33.0.1750.146+BIDUBrowser/6.x+Safari/537.36",
	"Mozilla/5.0+(Windows+NT+6.1)+AppleWebKit/537.36+(KHTML,+like+Gecko)+Chrome/39.0.2171.99+Safari/537.36+2345Explorer/6.5.0.11018",
	"Mozilla/5.0+(Windows+NT+6.2;+WOW64)+AppleWebKit/537.36+(KHTML,+like+Gecko)+Chrome/42.0.2311.154+Safari/537.36+LBBROWSER"
]


#默认的最大抓取间隔
time_max_delay = 6

#最小抓取间隔
time_min_delay = 3

#单站点最大并发抓取
max_requests_count = 4

#单站点最小抓取并发数
min_requests_count = 2

#first request url
first_url = r'https://movie.douban.com'

#需要抓取的站点的主域
domain = [r'https://movie.douban.com']

