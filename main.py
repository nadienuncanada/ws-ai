import asyncio
from scraper_utilis import (get_llm_strategy, fetch_data)
from crawl4ai import AsyncWebCrawler, BrowserConfig
import config

    
async def main():
  llm_strategy = get_llm_strategy()

  numero_de_pagina = 26

  browser_cfg = BrowserConfig(browser_type="chromium", headless=False, verbose=True)
  
  async with AsyncWebCrawler(config=browser_cfg) as crawler:
    while True:
        no_resultados= await fetch_data(llm_strategy, numero_de_pagina, url=config.URL_TO_SCRAPE, crawler=crawler )
        if no_resultados:
            print("No hay más resultados.")
            break
    numero_de_pagina += 1
    print(f"Procesando página {numero_de_pagina}...")
    await asyncio.sleep(2)  

if __name__ == "__main__":
    asyncio.run(main())