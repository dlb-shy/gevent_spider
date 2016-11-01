#-*-coding:utf-8-*-
#!/usr/bin python
from collections import defaultdict

def default_input_processor(value):
	value = value[0] if value \
	        else ''
	return value

def default_output_processor(value):
	return ''.join(value).encode('utf-8')

class Extract(object):
	def __init__(self, item, text, selector):
		self.sel = selector(text=text, type='html')
		self.item = item
		self.item_list = []
		self.link_set = set()
		self.local_item = defaultdict(list)

	def item_xpath(self, fieldname, xpath):
		#提取结构化数据
		value = self.sel.xpath(xpath).extract()
		input_process = self.get_input_process(fieldname)
		value = input_process(value)		
		self.item_list.append((fieldname, value))

	def link_xpath(self, xpath, re_patten=r'.'):
		#提取链接
		links = self.sel.xpath(xpath).re(re_patten)
		self.link_set.update(links)
		
	def get_item(self):
		#得到最终的结构化数据
		for k, v in self.item_list:
			self.local_item[k].append(v)
		for k, v in self.local_item.items():
			output_process = self.get_output_process(k)
			self.local_item[k] = output_process(v)
		return self.local_item

	def get_links(self):
		return list(self.link_set)

	def get_input_process(self, fieldname):
		process = getattr(self.item, fieldname).get('process_in',
			                             default_input_processor)
		
		return process
		
	def get_output_process(self, fieldname):
	    process = getattr(self.item, fieldname).get('process_out',
	    	                             default_output_processor)
	    
	    return process
