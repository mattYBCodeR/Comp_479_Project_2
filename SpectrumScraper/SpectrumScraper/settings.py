
BOT_NAME = "SpectrumScraper"

SPIDER_MODULES = ["SpectrumScraper.spiders"]
NEWSPIDER_MODULE = "SpectrumScraper.spiders"

ADDONS = {}

# Obey robots.txt rules
ROBOTSTXT_OBEY = True


# I ADDED THIS
# ITEM_PIPELINES = {"scrapy.pipelines.files.FilesPipeline": 1}
# FILES_STORE = "downloaded_pdfs"

# Concurrency and throttling settings
#CONCURRENT_REQUESTS = 16
CONCURRENT_REQUESTS_PER_DOMAIN = 1
DOWNLOAD_DELAY = 1

FEED_EXPORT_ENCODING = "utf-8"
