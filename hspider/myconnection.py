#-*-coding:utf-8-*-
#!/usr/bin python

import redis
import MySQLdb
import my_settings

class MySQLConnect(object):
	"""
	建立到MySQL的连接
	该类主要用于继承
	"""
	def __init__(self, host=my_settings.mysql_host, password=my_settings.mysql_password, 
		         username=my_settings.mysql_username, database=my_settings.mysql_database,
		         charset=my_settings.charset):
		self.connect = MySQLdb.connect(host=host, user=username, 
			                           passwd=password, db=database)
		self.cousor = self.connect.cursor()

class RedisConnect(object):
	"""
	建立到redis的连接
	该类主要用于继承
	"""
	def __init__(self, host=my_settings.redis_host, port=my_settings.redis_port, 
		         db=my_settings.redis_db):
		self.pool = redis.ConnectionPool(host=host, port=port, db=db)
		self.r = redis.StrictRedis(connection_pool=self.pool)