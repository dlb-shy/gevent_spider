#-*-coding:utf-8-*-
from collections import defaultdict

class Extract(object):
	def __init__(self, text, selector):
		self.sel = selector(text=text, type='html')
		self.item_list = []
		self.link_set = set()
		self.local_item = defaultdict(list)

	def item_xpath(self, fieldname, xpath):
		#提取结构化数据
		value = self.sel.xpath(xpath).extract()
		#提取出来的数据是一个列表,为空或者包含一个元素
		#如果列表不为空，就把这个元素拿出来
		#否则就赋予一个空字符串
		item = (fieldname, value[0]) if value \
		        else (fieldname, '')		
		self.item_list.append(item)

	def link_xpath(self, xpath, re_patten=r'.'):
		#提取链接
		links = self.sel.xpath(xpath).re(re_patten)
		self.link_set.update(links)
		
	def get_item(self):
		for k, v in self.item_list:
			self.local_item[k].append(v)
		for k, v in self.local_item.items():
			self.local_item[k] = ','.join(v).encode('utf-8')
		return self.local_item

	def get_links(self):
		return list(self.link_set)
