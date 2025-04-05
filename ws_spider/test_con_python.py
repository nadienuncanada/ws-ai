from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
#from ws_spider.spiders.example_spider import ExampleSpider
from spiders.example_spider import ExampleSpider


def crawler_func_li_next(spider, response):
    next_page = response.css('li.next a::attr(href)').get()
    if next_page:
        yield response.follow(next_page, callback=spider.parse)

archivo_salida = "data/example.json"
#CLOSESPIDER_PAGECOUNT = 3
#CLOSESPIDER_ITEMCOUNT = 50,

process = CrawlerProcess(settings={
    "FEEDS": {
        archivo_salida : {"format": "json", "overwrite": True},
    },
    #"CLOSESPIDER_PAGECOUNT": CLOSESPIDER_PAGECOUNT,
    # "CLOSESPIDER_ITEMCOUNT": CLOSESPIDER_ITEMCOUNT,
})

urls = "https://quotes.toscrape.com/page/1/"
process.crawl(ExampleSpider, start_urls=urls, crawler_func=crawler_func_li_next)
process.start()
