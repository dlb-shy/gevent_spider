#-*-coding:utf-8-*-
#!/usr/bin python

import json
import redis
import pymysql
from sqlalchemy import create_engine
import config


"""dialect+driver://username:password@host:port/database"""
_URL = 'mysql+pymysql://root:lymlhhj123@127.0.0.1/douban'

myconfig = {'pool_recycle': 3600,
		  'encoding': 'utf-8', 
		  'pool': None,
		  'poolclass': None,
		  'pool_size': 5,
		  'echo': False,
		  'echo_pool': False,
		  'max_overflow': 10, 
		  'pool_timeout': 30,}

class MySQL(object):
	def __init__(self):
		self.db = create_engine(name_or_url=_URL, **myconfig)

	def _get_connection(self):
		conn = self.db.connect()
		return conn

	def select(self, cmd, item=()):
		"""
		对数据库不会造成状态改变的就用这条语句
		比如: select()
		"""
		cnx = self._get_connection()
		#下面返回的middle类似于游标
		#所以需要调用fetchall()才可以获得结果
		#调用close()就会把连接释放回连接池
		middle = cnx.execute(cmd, item)
		result = middle.fetchall()
		cnx.close()
		return result

	def query(self, cmd, item=()):
		"""
		对数据库会造成状态改变的就用这条语句
		比如: insert()
		"""
		cnx = self._get_connection()
		cnx.execute(cmd, item)
		
		cnx.close()

	def close(self):
		"""
		dispose()::::::
		Dispose of the connection pool used by this Engine.

		This has the effect of fully closing all currently checked in database connections. 
		Connections that are still checked out will not be closed, 
		however they will no longer be associated with this Engine, 
		so when they are closed individually, 
		eventually the Pool which they are associated with will be garbage collected and they will be closed out fully, 
		if not already closed on checkin.

		A new connection pool is created immediately after the old one has been disposed. 
		This new pool, like all SQLAlchemy connection pools, 
		does not make any actual connections to the database until one is first requested, 
		so as long as the Engine isn’t used again, no new connections will be made.

		When a program uses multiprocessing or fork(), 
		and an Engine object is copied to the child process, 
		Engine.dispose() should be called so that the engine creates brand new database connections local to that fork. 
		Database connections generally do not travel across process boundaries.
		"""
		self.db.dispose()



class RedisConnect(object):
	"""
	建立到redis的连接
	该类主要用于继承
	"""
	def __init__(self, **kwargs):
		self.pool = redis.ConnectionPool(**kwargs)
		self.r = redis.StrictRedis(connection_pool=self.pool)

	def lindex(self, keyname):
		result = self.r.lindex(keyname, 0)
		return result

	def rpush(self, keyname, item):
	
		self.r.rpush(keyname, item)
		

	def lpush(self, keyname, item):				
		self.r.lpush(keyname, item)
		

	def brpop(self, keyname):
		item = json.loads(self.r.brpop(keyname, 0)[1])
		return item

	def blpop(self, keyname):
		#从redis服务器的url_queue中取出一个item,取出的是一个元组对，
		#第一个元素是队列的名字（即'url_queue'），第二个才是目标元素
		item = json.loads(self.r.blpop(keyname, 0)[1])
		return item

