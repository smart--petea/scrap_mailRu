# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field

class MailRuItem(Item):
	# define the fields for your item here like:
	# name = Field()
	ffrom = Field()
	fromName = Field()
	DateFull = Field()
	id = Field()
	subject = Field()
	let_body_plain = Field()
	AttachmentContent = Field()
	AttachmentName = Field()
	AttachmentType = Field()
