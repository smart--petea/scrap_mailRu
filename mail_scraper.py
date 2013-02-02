from scrapy.settings import CrawlerSettings
import argparse
from mail_ru import settings
from scrapy import log
import sys
from scrapy.crawler import CrawlerProcess

#I need to modify a litle the existent object for realize a transmiting mechanism of settings

class MyCrawlerSettings(CrawlerSettings):
	def __setitem__(self, opt_name, val_name):
		self.values[opt_name] =  val_name
	def __contains__(self, item):
		#print(type(item))
		return True if CrawlerSettings.__getitem__(self, item) else False
		
parser = argparse.ArgumentParser()
#parser.add_argument("EMAILAddress", help="email address for parsing")
parser.add_argument("EMAILLogin", help="email login")
parser.add_argument("EMAILPasswd", help="email password")
parser.add_argument("-MyDbHost", help="The host")
parser.add_argument("-MyDbUser", help="The database user name")
parser.add_argument("-MyDbPasswd", help="The database user passwd")
parser.add_argument("-MyDbName", help="The database name")

args = parser.parse_args()


MySettings = MyCrawlerSettings(settings_module=settings)
#MySettings['EMAILAddress'] = args.EMAILAddress
MySettings['EMAILLogin'] = args.EMAILLogin
MySettings['EMAILPasswd'] = args.EMAILPasswd
MySettings['MyDbName'] = args.MyDbName or 'mail_ru'
MySettings['MyDbHost'] = args.MyDbHost or 'localhost'
MySettings['MyDbUser'] = args.MyDbUser or "root"
MySettings['MyDbPasswd'] = args.MyDbPasswd or 'kate'

MyCrawler = CrawlerProcess(MySettings) 


MyCrawler.configure() #podgotovka vnutrenostei crawlera
#print("Start from _ crawler")
log.start_from_crawler(MyCrawler)
#print("Crawl the spiders")

for spider_object in MyCrawler.spiders._spiders.itervalues():
	MyCrawler.crawl(spider_object())
print("\nNachali\n")
MyCrawler.start()
log.msg(message="poka", _level = log.INFO)
