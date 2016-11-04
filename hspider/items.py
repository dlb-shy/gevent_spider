#-*-coding:utf-8-*-
#!/usr/bin python
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

"""
可以在每个字段里面定义函数，用来处理提取到的item
比如
def takefirst(value):
	return value[0]

def join(value):
	return ''.join(value)

class Item(object):
	movie_name = dict(process_in=takefirst, process_out=join)
	movie_year = dict()
	movie_type = dict()
	movie_rate = dict()
"""

class Item(object):
	movie_name = dict()
	movie_year = dict()
	movie_type = dict()
	movie_rate = dict()

