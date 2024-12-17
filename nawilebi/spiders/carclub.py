import scrapy
from nawilebi.items import NawilebiItem
from urllib.parse import urlparse, parse_qs
import re
import requests
from bs4 import BeautifulSoup


class CarclubSpider(scrapy.Spider):
    name = "carclub"
    allowed_domains = ["carclub.ge"]
    start_urls = ["https://carclub.ge/"]
    custom_settings = {
        'ITEM_PIPELINES': {
            "nawilebi.pipelines.NawilebiPipeline": 100,
            "nawilebi.pipelines.CarclubPipeline": 200,
            "nawilebi.pipelines.SaveToMySQLPipeline": 900
        },
        'DOWNLOAD_DELAY': 0.5,
    }

    def extract_make_model(self, url):
        # Parse the URL
        parsed_url = urlparse(url)
        
        # Parse the query parameters
        query_params = parse_qs(parsed_url.query)
        
        # Extract make and model values
        car_make = query_params.get('_make', [None])[0]  # Retrieves 'Toyota'
        car_model = query_params.get('_model', [None])[0]  # Retrieves 'CAMRY'
        
        return car_make.upper(), car_model.upper()
    
    def parse(self, response):
        car_mark_url_list = response.css("div.entry-content div:nth-of-type(3) > div div div a::attr(href)").getall()
        
        for car_mark_url in car_mark_url_list:
            
            yield response.follow(car_mark_url, callback = self.parse_mark_page)
            
    def parse_mark_page(self, response):
        car_model_url_list = list(set(response.css("div.entry-content div.wp-block-stackable-columns > div > div > div a::attr(href)").getall()))
        
        for car_model_url in car_model_url_list:
            
            yield response.follow(car_model_url, callback = self.parse_model_page)
            
    def parse_model_page(self, response):
        
        part_list = response.css("section ul li.product")
        '''car_mark, car_model = self.extract_make_model(response.url)
        year_pattern = re.compile(r'(\d{2,4})\s*-\s*(\d{0,4})')
        start_year = None
        end_year = None
        year = None'''
        
        for part in part_list:
            part_url = part.css("a.woocommerce-LoopProduct-link::attr(href)").get()
            
            yield response.follow(part_url, callback = self.parse_part_page)
            
    
    def parse_part_page(self, response):
        
        item = NawilebiItem()
        
        item["website"] = "https://carclub.ge/"
        item["phone"] = "551 94 49 33"
        item["part_full_name"] = response.css("div.summary.entry-summary h1::text").get()
        item["price"] = response.css("div.summary.entry-summary p.price span bdi::text").get()
        item["car_mark"] = response.css("div.ymm-vehicle-fitment table tr:nth-of-type(2) td:nth-of-type(1)::text").get().strip().upper()
        item["car_model"] = response.css("div.ymm-vehicle-fitment table tr:nth-of-type(2) td:nth-of-type(2)::text").get().strip().upper()
        year = response.css("div.ymm-vehicle-fitment table tr:nth-of-type(2) td:nth-of-type(3)::text").get().strip().upper()
        year_pattern = re.compile(r'(\d{2,4})\s*-\s*(\d{0,4})')
        start_year = None
        end_year = None 
        match =  re.search(year_pattern, year)
        if match:
            start_year = match.group(1)
            end_year = match.group(2)
            
        item["start_year"] = start_year
        item["end_year"] = end_year
        
        yield item