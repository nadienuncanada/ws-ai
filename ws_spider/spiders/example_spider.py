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
        for quote in response.css('div.quote'):
            yield {
                'text': quote.css('span.text::text').get(),
                'author': quote.css('small.author::text').get(),
            }
        
        
        if self.crawler_func:
            for result in self.crawler_func(self, response):
                yield result

