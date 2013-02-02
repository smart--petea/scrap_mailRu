"""
HostMiddleware: populates Request host field, based on the Response which originated it
"""

from scrapy.http import Request
from scrapy.exceptions import NotConfigured

class HostMiddleware(object):
	
	@classmethod
	def from_crawler(cls, crawler):
		return cls()

	def process_spider_output(self, response, result, spider):
		def _set_host(r):
			if isinstance(r, Request):
				r.headers.setdefault('Host', r.url)
			return r
		return (_set_host(r) for r in result or ())
