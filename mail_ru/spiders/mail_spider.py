from scrapy.spider import BaseSpider
from scrapy.http import Request, FormRequest
from scrapy.selector import HtmlXPathSelector
from scrapy import log
from mail_ru.items import MailRuItem
import json, re
reForExtract = re.compile(r'"(//e.mail.ru/cgi-bin/getattach\?[^\"]*")')
reAttachName = re.compile(r'name="([^\"]*)"')
reNextPage   = re.compile(r'(?<=class="paging__item paging__item_next icon icon_paging-horizontal).*?href="(msglist[^"]*)"')

import re, sys, os, time, json
FindId = re.compile(r'\bId:.*"(\d+)"')

class mail_spider(BaseSpider):
	name = 'mail_spider'
	start_urls = ['http://www.mail.ru']
	domain = 'mail.ru'

	#login = self.crawler.settings['EMAILLogin']#'smart__petea
	#password = self.crawler.settings['EMAILPasswd']#'badarau'

	def parse(self, response):
		log.msg(message = "Mail_Spider: Authentication stage", _level = log.INFO)
		login = self.crawler.settings['EMAILLogin']
		self.useremail=login + '@mail.ru'
		password = self.crawler.settings['EMAILPasswd']
		FirstOfficialRedirect = FormRequest('https://auth.mail.ru/cgi-bin/auth',  callback=self.parse_FirstOfficialRedirect, formdata={'Domain': self.domain, 'Login': login, 'Password': password, 'level': '0'})
		yield FirstOfficialRedirect



	def parse_FirstOfficialRedirect(self, response):
		if response.status // 100 != 2:
			log.msg(message = "Mail_Spider: parse_FirstOfficialRedirect function - wrong response status %d " % response.status, _level = log.ERROR)
			return
		
		
		log.msg(message = "Mail_Spider: the spider is authorized", _level = log.INFO)
		FirstPageRequest = Request('https://e.mail.ru/cgi-bin/msglist?back=1', callback=self.parse_PageRequest)
		yield FirstPageRequest

	def parse_PageRequest(self, response):
		log.msg(message = "Mail_Spider: parse_PageRequest function", _level = log.INFO)
		ListOfId = FindId.findall(response.body)
		#I'm going to parse all messages from the mail mail page
		for PARAM in ListOfId:
			yield FormRequest("https://e.mail.ru/cgi-bin/readmsg", callback=self.parse_EmailBody, formdata={"AvStatusBar": '1', "NewAttachViewer": '1', 'ajax_call': '1', 'bulk_show_images': '0', 'folder': '0', 'func_name': 'get_messages_by_id', 'id': PARAM, 'let_body_type': 'let_body_plain', 'log': '1', 'multi_msg_prev': '0', 'no_rnb': 'Y', 'now': str(time.time()* 1000), 'read': PARAM, 'sortby': 'D', 'x-email': self.useremail})
		try:
			NextPageUrl = reNextPage.search(response.body).group(1)
		except AttributeError:
			pass
		except Exception as e:
			log.msg(message="Mail_Spider: parse_PageRequest function Error: " + str(e) + " " + str(e.__repr__), _level = log.ERROR)
		else:
			NextPageUrl = "https://e.mail.ru/cgi-bin/" + NextPageUrl
			print(NextPageUrl)
			yield Request(NextPageUrl, callback=self.parse_PageRequest)

	def parse_EmailBody(self, response):
		##!! proverka statusa
		
		##!! proverka validnosti json
		var_date = json.loads(response.body)[2][0]
		item = MailRuItem()
		item['ffrom'] = var_date['From']
		item['fromName'] = var_date['FromName']
		item['id'] = var_date['Id']
		item['subject'] = var_date['Subject']
		item['let_body_plain'] = var_date['let_body_plain']
		item['DateFull'] = var_date['DateFull']
		print("Email body: ", var_date['Id'])

		yield item
		
		#if there exists some attachments I'll extract it
		ForExtract = reForExtract.findall(var_date['Attachment_html'])	
		for attach in ForExtract:
			yield Request('https:' + attach, callback=self.parse_Attach, meta={'id': var_date['Id']})	

	def parse_Attach(self, response):
		if response.status // 100 != 2:
			return

	
		item = MailRuItem()
		item['id'] = response.meta['id']
		item['AttachmentContent'] = response.body
		index = response.headers['Content-Type'].find(';')
		if index != -1:
			item['AttachmentType'] = response.headers['Content-Type'][:index]
		else:
			item['AttachmentType'] = response.headers['Content-Type']
		
		try:
			item['AttachmentName'] = reAttachName.search(response.headers['Content-Type']).group(1)
		except AttributeError:
			item['AttachmentType'] = 'secret'
		print("Email id: ", item['id'], " attachfile: ", item['AttachmentName'])
		yield item
