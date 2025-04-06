import scrapy

class ExampleSpider(scrapy.Spider):
    name = "example"

    def __init__(self, start_urls=None, crawler_func=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if start_urls:
            self.start_urls = start_urls.split(',')
        else:
            self.start_urls = ['https://quotes.toscrape.com/']

        self.crawler_func = crawler_func

    def parse(self, response):
        articles = response.xpath('/html/body/div/main/div/div/section[2]/div[2]/div/article')
        for article in articles:
            yield {
                'nombre': article.xpath('.//header/h4/text()').get(),
                'tipo': article.xpath('.//div/text()[1]').get()
            }
        
        if self.crawler_func:
            for result in self.crawler_func(self, response):
                yield result

