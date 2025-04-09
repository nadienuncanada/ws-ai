from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from spiders.craw4ia_spider import Craw4iaSpider


'''def crawler_func_li_next(spider, response):
    next_page = response.css('li.next a::attr(href)').get()
    if next_page:
        yield response.follow(next_page, callback=spider.parse)

        
def crawler_func_data_qa_PAGING_NEXT(spider, response):
    next_page = response.css('a.paging-module__page-arrow[data-qa="PAGING_NEXT"]::attr(href)').get()
    if next_page:
        yield response.follow(next_page, callback=spider.parse)'''

        
def crawler_func_a_contains_NEXT(spider, response):
    next_page = response.xpath('//a[contains(text(), "Next")]/@href').get()
    if next_page:
        yield response.follow(next_page, callback=spider.parse)

archivo_salida = "data/huggingface_models.json"
CLOSESPIDER_PAGECOUNT = 3
#CLOSESPIDER_ITEMCOUNT = 50,

process = CrawlerProcess(settings={
    "FEEDS": {
        archivo_salida : {"format": "json", "overwrite": True},
    },
    "CLOSESPIDER_PAGECOUNT": CLOSESPIDER_PAGECOUNT,
    # "CLOSESPIDER_ITEMCOUNT": CLOSESPIDER_ITEMCOUNT,
})

urls = "https://huggingface.co/models" # config.URL_TO_SCRAPE
instruction = "Extrae los siguientes datos  'Nombre de modelo', 'Categoria del modelo' ,'Ultima actualizacion del modelo', de los siguientes datos que consegui de una pagina web. Devuelve el resultado en formato JSON." # config.INSTRUCTION_TO_LLM
process.crawl(Craw4iaSpider, start_urls=urls, instruction=instruction, crawler_func=crawler_func_a_contains_NEXT)

process.start()
