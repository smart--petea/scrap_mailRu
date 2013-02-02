#-*- coding: utf8 -*-
#Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.xlib.pydispatch import dispatcher
from scrapy import signals
from scrapy.exceptions import DropItem
import MySQLdb
from collections import defaultdict
from scrapy import log

class MailRuPipeline(object):
	def __init__(self):
		self.fields_to_export = ['From', 'FromName', 'DateFull', 'Id', 'Subject', 'let_body_plain', 'AttachmentContent', 'AttachmentName', 'AttachmentType'] 
		dispatcher.connect(self.spider_opened, signals.spider_opened)
		dispatcher.connect(self.spider_closed, signals.spider_closed)
		self.spiders = defaultdict(dict)

	def spider_opened(self, spider):
		log.msg(message="MailRuPipeline: Our sharashka is opend", _level = log.INFO)
		print("\n\nSPIDER OPENED\n\n")
		dbStructure = {'message':{\
									'id': ('VARCHAR(30)', 'NOT NULL', 'PRIMARY KEY'),\
									'ffrom': ('VARCHAR(30)',),\
									'fromName': ('VARCHAR(30)',),\
									'dateFull': ('VARCHAR(30)',),\
									'subject': ('VARCHAR(30)',),\
									'let_body_plain': ('VARCHAR(1500)',),\
								  }, \
						'attachment': {\
									'id': ('VARCHAR(30)','REFERENCES message(id)',),\
									'content': ('MEDIUMBLOB',),\
									'name': ('VARCHAR(30)', 'UNIQUE'), \
									'type': ('VARCHAR(30)',),\
								  }\
					   }
		#initialize the spider's date
		SpiderName = spider.name
		Settings = spider.crawler.settings
		DbName = self.spiders[SpiderName]['MyDbName'] = Settings['MyDbName']
		self.spiders[SpiderName]['MyDbHost'] = Settings['MyDbHost']
		self.spiders[SpiderName]['MyDbUser'] = Settings['MyDbUser']
		self.spiders[SpiderName]['MyDbPasswd'] = Settings['MyDbPasswd']
		
		try:
			self.spiders[SpiderName]['MyDbConnect'] = MySQLdb.connect(host = self.spiders[SpiderName]['MyDbHost'], user = self.spiders[SpiderName]['MyDbUser'], passwd = self.spiders[SpiderName]['MyDbPasswd'], charset = "utf8")
		except Exception as e:
			log.msg(message="MailRuPipeline: Can't connect to Data Base" + str(e), _level=log.ERROR)
			spider.crawler.stop()
			return



		cursor = self.spiders[SpiderName]['MyDbCursor'] = self.spiders[SpiderName]['MyDbConnect'].cursor()
		#It's Ok I have a connection to MySQL data base
		#I'm going to verify if data base MyDbName exist 
		#If that DB exist I verify if structure is a good for us
		#If that DB don't exist I'll create
		try:
			cursor.execute("CREATE DATABASE %s" % DbName)
		except MySQLdb.ProgrammingError as e:
			if e[0] != 1007: 
				log.msg(message="MailRuPipeline: can't create database Error: " + str(e), _level=log.ERROR)
				spider.crawler.stop()
				return

			#the database exists, It's Ok
			log.msg(message="MailRuPipeline: database %s exist" % DbName, _level = log.INFO)
			#Here I must verify the structure correspondence with my point of view
			cursor.execute("USE %s " % DbName)
			cursor.execute("SHOW TABLES")
			TableMustBe = set(dbStructure.keys()).difference({x[0] for x in cursor.fetchall()})
			if TableMustBe:
				log.msg(message  = "MailRuPipeline: the existent database has different structure", _level = log.ERROR)
				spider.crawler.stop()
				return
			#next I verify the each table's structure
			try:
				for table in dbStructure:
					cursor.execute('DESCRIBE %s' %table)
					FieldFromDb = {x[0] for x in cursor.fetchall()}	
					Rez =  set(dbStructure[table].keys()).difference(FieldFromDb)
					if Rez:
						log.msg(message = "MailRuPipeline: the table %s haven't the fields %s " % (table, str(Rez)))
						spider.crawler.stop()
						return
			except Exception as e:
				log.msg(message="MailRuPipeline: unknown error Error: " + str(e), _level = log.ERROR)
				spider.crawler.stop()
				return

		except Exception as e:
			log.msg(message="MailRuPipeline: unknown error Error: " + str(e),   _level = log.ERROR)
			spider.crawler.stop()
			return
		else:
			cursor.execute("USE %s" % DbName)
			log.msg(message="MailRuPipeline: attempt to create a new database", _level = log.INFO)
			for table in dbStructure:
				list1 = (field + ' ' + ' '.join(dbStructure[table][field]) for field in dbStructure[table])	
				strCommand = ', '.join(list1) 
				strCommand = table + ' (' + strCommand + ') DEFAULT CHARACTER SET UTF8'
				#print("CREATE TABLE " + strCommand)
				cursor.execute("CREATE TABLE " + strCommand)
			log.msg(message="MailRuPipeline: new database %s is created" % DbName)


				

			
			
			

	def process_item(self, item, spider):
		log.msg(message = "MailRuPipeline: the pipeline get the item")
		#There are tho models of item
		#The item that describe the email body
		#The item that describe the attachment of email
		cursor = self.spiders[spider.name]['MyDbCursor']
		connect = self.spiders[spider.name]['MyDbConnect']
		try:
			if not item.get('AttachmentContent', False):
				cursor.execute( "INSERT INTO message(id, ffrom, fromName, dateFull, subject, let_body_plain) VALUES(%s, %s, %s, %s, %s, %s)", (\
												item.get('id'), \
												item.get('ffrom'), \
												item.get('fromName'), \
												item.get('DateFull'), \
												item.get('subject'), \
												item.get('let_body_plain')))
				#print(strC)
				#import os
				#fd  = os.open('pipeline.fd', os.O_CREAT | os.O_TRUNC | os.O_WRONLY)
				#os.write(fd, strC)
				#os.close(fd)

				#cursor.execute(strC)
			else:

				print("INSERT intor attachment")
				cursor.execute("INSERT INTO attachment(id, name, type, content) VALUES(%s, %s, %s, %s)", (item.get('id'), item.get('AttachmentName'), item.get('AttachmentType'), MySQLdb.escape_string(item.get('AttachmentContent'))))
				#cursor.execute("INSERT INTO attachment(id, name, type) VALUES(%s, %s, %s)", (item.get('id'), item.get('AttachmentName'), item.get('AttachmentType')))

				print("It's OK")
		except MySQLdb.IntegrityError:
			raise DropItem
		except Exception as e:
			print("ERROR: ", str(e))
			log.msg(message = "MailRuPipeline - process_item: unknown error: %s" % str(e), _level = log.ERROR)
			raise DropItem
		else:
			connect.commit()
			return item

	def spider_closed(self, spider):
		pass
