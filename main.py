import asyncio
import json
import os
from typing import List
from crawl4ai import AsyncWebCrawler, BrowserConfig, CacheMode, CrawlerRunConfig, LLMConfig
from crawl4ai.extraction_strategy import LLMExtractionStrategy
from pydantic import BaseModel, Field
import config
from dotenv import load_dotenv

load_dotenv()

class Product(BaseModel):
    model: str
    score: str
    organization: str
    rank: str

async def main():
    
    
    llm_strategy = LLMExtractionStrategy(
        llm_config = LLMConfig(
        provider="groq/deepseek-r1-distill-llama-70b",
        api_token=os.getenv("GROQ_API_KEY"),
    ),
        schema=Product.model_json_schema(),
        extraction_type="schema",
        instruction=config.INSTRUCTION_TO_LLM,
        chunk_token_threshold=1000,
        overlap_rate=0.0,
        apply_chunking=True,
        input_format="markdown",
    )


    crawl_config = CrawlerRunConfig(
        extraction_strategy=llm_strategy,
        cache_mode=CacheMode.BYPASS,
        process_iframes=False,
        remove_overlay_elements=True,
        # css_selector="[class^='p-4']",
        exclude_external_links=True,
    )

    browser_cfg = BrowserConfig(browser_type="chromium", headless=False, verbose=True)

    async with AsyncWebCrawler(config=browser_cfg) as crawler:

        result = await crawler.arun(url=config.URL_TO_SCRAPE, config=crawl_config)

        if result.success:
            #result!= "No hay mas paginas"
            
            data = json.loads(result.extracted_content)

            print("Extracted items:", data)

            llm_strategy.show_usage()
            with open("data/data.json", "w", encoding="utf-8") as f:
              f.write(result.extracted_content)
        else:
            print("Error:", result.error_message)
        

if __name__ == "__main__":
    asyncio.run(main())