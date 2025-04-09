import os
import scrapy
import asyncio
import nest_asyncio
from pydantic import BaseModel, Field
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, LLMConfig, BrowserConfig, CacheMode
from crawl4ai.extraction_strategy import LLMExtractionStrategy
from typing import Dict

nest_asyncio.apply()


class OpenAIModelFee(BaseModel):
    model_name: str = Field(..., description="Name of the OpenAI model.")
    input_fee: str = Field(..., description="Fee for input token for the OpenAI model.")
    output_fee: str = Field(
        ..., description="Fee for output token for the OpenAI model."
    )

class Craw4iaSpider(scrapy.Spider):
    name = "craw4ia_spider"

    def __init__(self, start_urls:str = None, instruction:str = None, crawler_func=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if start_urls:
            self.start_urls = start_urls.split(',')
        else:
            self.start_urls = ['https://quotes.toscrape.com/']

        self.instruction = instruction
        self.crawler_func = crawler_func

    def parse(self, response):
        # Obtener la URL actual
        url = response.url

        # Ejecutar Crawl4AI de forma asincrónica
        loop = asyncio.get_event_loop()
        data = loop.run_until_complete(
            self.extract_structured_data_using_llm(
                            url=url,
                            instruction = self.instruction, 
                            provider="groq/deepseek-r1-distill-llama-70b", 
                            api_token=os.getenv("GROQ_API_KEY")
            )
        )

        # Procesar los datos extraídos
        for item in data:
            yield item
        
        if self.crawler_func:
            for result in self.crawler_func(self, response):
                yield result


    async def extract_structured_data_using_llm(
        self,
        url: str = "https://openai.com/api/pricing/", 
        instruction: str = """From the crawled content, extract all mentioned model names along with their fees for input and output tokens. Do not miss any models in the entire content.""" , 
        provider: str = "ollama", 
        api_token: str = None, 
        extra_headers: Dict[str, str] = None
    ):
        print(f"\n--- Extracting Structured Data with {provider} ---")

        if api_token is None and provider != "ollama":
            print(f"API token is required for {provider}. Skipping this example.")
            return

        browser_config = BrowserConfig(headless=True)

        extra_args = {"temperature": 0, "top_p": 0.9, "max_tokens": 2000}
        if extra_headers:
            extra_args["extra_headers"] = extra_headers

        crawler_config = CrawlerRunConfig(
            cache_mode=CacheMode.BYPASS,
            word_count_threshold=1,
            page_timeout=80000,
            extraction_strategy=LLMExtractionStrategy(
                llm_config = LLMConfig(provider=provider,api_token=api_token),
                schema=OpenAIModelFee.model_json_schema(),
                extraction_type="schema",
                instruction=instruction,
                extra_args=extra_args,
            ),
        )

        async with AsyncWebCrawler(config=browser_config) as crawler:
            result = await crawler.arun(
                url=url, config=crawler_config
            )
            #return [{"extracted_content": result.extracted_content, "cleaned_text": result.cleaned_text}]
            return [{"extracted_content": result.extracted_content}]
            