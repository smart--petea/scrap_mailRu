# Scrapy settings for mail_ru project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'mail_ru'

SPIDER_MODULES = ['mail_ru.spiders']
NEWSPIDER_MODULE = 'mail_ru.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'mail_ru (+http://www.yourdomain.com)'
#COOKIES_DEBUG = True
DEFAULT_REQUEST_HEADERS = {'Connection': 'keep-alive'}
#REDIRECT_ENABLED = False
REDIRECT_MAX_METAREFRESH_DELAY = -1
SPIDER_MIDDLEWARES = {'mail_ru.spidermiddleware.host.HostMiddleware' : 750}
ITEM_PIPELINES = ['mail_ru.pipelines.MailRuPipeline']
LOG_FILE = "crawl.log"
