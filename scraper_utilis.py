from typing import List, Tuple
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from crawl4ai import CacheMode, CrawlerRunConfig, LLMConfig
from crawl4ai.extraction_strategy import LLMExtractionStrategy
import config
import os
from pydantic import BaseModel, Field
import json

load_dotenv()

def get_crawler_config() -> CrawlerRunConfig:
    
    return CrawlerRunConfig(
        extraction_strategy=get_llm_strategy(),
       # css_selector=config.CSS_SELECTOR,#le especifico que class tiene que ver y que no, para no traer informacion de mas. HAY QUE VER SI SIRVE
        cache_mode=CacheMode.BYPASS,
        process_iframes=False,
        remove_overlay_elements=True,
        exclude_external_links=True,
    )

def get_llm_strategy() -> LLMExtractionStrategy:
     return LLMExtractionStrategy(
        llm_config = LLMConfig(
        provider="groq/llama-guard-3-8b",
        api_token=os.getenv("GROQ_API_KEY"),
    ),
        schema=Alquiler.model_json_schema(),
        extraction_type="schema",
        instruction=config.INSTRUCTION_TO_LLM,
        chunk_token_threshold=1000,
        overlap_rate=0.0,
        apply_chunking=True,
        input_format="markdown",
    )
     
async def fetch_data(llm_strategy, numero_de_pagina, url,crawler):
  url = f"{url}{numero_de_pagina}.html"
  print(f"URL a procesar: {url}")
  no_result = await check_results (url=url, crawler=crawler)
  if no_result:
    return True #si no hay resultado mandamos True.
  print("Pase el no_result, voy a la ia")
  result = await crawler.arun(
      url=url,
      config=CrawlerRunConfig(
        extraction_strategy=llm_strategy,
        cache_mode=CacheMode.BYPASS,
        process_iframes=False,
        remove_overlay_elements=True,
        exclude_external_links=True,
      ),
  )
  if not(result.success and result.extracted_content):
    print("No se pudo extraer contenido o no hay resultados.")
    return False
  new_data = json.loads(result.extracted_content)
  print("Datos extraídos:", new_data)
  llm_strategy.show_usage()

  #   # Ruta del archivo JSON
  # file_path = "data/data.json"

  #   # Cargar datos existentes si el archivo ya tiene información
  # if os.path.exists(file_path):
  #       with open(file_path, "r", encoding="utf-8") as f:
  #           try:
  #               existing_data = json.load(f)  # Intentamos cargar los datos previos
  #               if not isinstance(existing_data, list):
  #                   existing_data = []  # Si no es una lista, inicializamos como lista vacía
  #           except json.JSONDecodeError:
  #               existing_data = []  # Si hay un error, inicializamos la lista vacía
  # else:
  #       existing_data = []  # Si el archivo no existe, empezamos con una lista vacía

  #   # Agregar los nuevos datos a la lista
  # existing_data.append(new_data)

  #   # Guardar todo nuevamente en el archivo
  # with open(file_path, "w", encoding="utf-8") as f:
  #       json.dump(existing_data, f, ensure_ascii=False, indent=4)  # Guardamos bonito
  return False  # Continuar la ejecución

async def check_results(url, crawler) -> bool:
    result = await crawler.arun(
        url=url,
        config=CrawlerRunConfig(cache_mode=CacheMode.BYPASS),  # No usamos LLM para ahorrar tokens
    )
    if result.success:
       soup = BeautifulSoup(result.cleaned_html, "html.parser")
      # Buscar todos los botones con la clase "paging-module__page-arrow" 
       buttons = soup.find_all("a", class_="paging-module__page-arrow")
      # Si hay menos de 2 botones, significa que falta el que buscamos
       if len(buttons) > 2:#si hay 2 botonoes, significa que hay una pagina mas
        return True
    return False
   
class Alquiler(BaseModel):
    alquiler: float
    expensas: float
    direccion: str
    ubicacion: str
    metros_cuadrados: float
    descripcion:str
    cant_ambientes: int
    cant_banos: int
    cant_dormitorios: int