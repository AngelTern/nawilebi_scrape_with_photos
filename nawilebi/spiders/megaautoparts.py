import scrapy
from nawilebi.items import NawilebiItem
import re
from urllib.parse import urlparse, parse_qs

class MegaautopartsSpider(scrapy.Spider):
    name = "megaautoparts"
    allowed_domains = ["megaautoparts.ge", "proxy.scrapeops.io"]  # Added "proxy.scrapeops.io"
    start_urls = ["https://megaautoparts.ge/"]
    custom_settings = {
        'ITEM_PIPELINES': {
            "nawilebi.pipelines.NawilebiPipeline": 300,
            "nawilebi.pipelines.OtopartsPipeline": 200,
            "nawilebi.pipelines.SaveToMySQLPipeline": 900
        },
        'SCRAPEOPS_PROXY_ENABLED': True,
        "DOWNLOADER_MIDDLEWARES": {
            "scrapeops_scrapy_proxy_sdk.scrapeops_scrapy_proxy_sdk.ScrapeOpsScrapyProxySdk": 100,
            "nawilebi.middlewares.FakeBrowserHeaderAgentMiddleware": 101,
            # Include other middlewares as needed
        },
        'DOWNLOAD_DELAY': 1.5,
        'AUTOTHROTTLE_ENABLED': True,
        'DOWNLOAD_TIMEOUT': 30,
        'RETRY_TIMES': 5,
        'RETRY_DELAY': 2,
        'RETRY_HTTP_CODES': [500, 502, 503, 504, 408],
    }

    def adjust_car_name_for_url_megaauto(self, string):
        string = string.lower()
    
        string = re.sub(r'\s+', '-', string)
    
        string = re.sub(r'[()]', '', string)
    
        string = re.sub(r'[^a-z0-9-]', '', string)
    
        return string
    
    def parse(self, response):
        car_mark_urls = response.css("#main > div > div > section.elementor-section.elementor-top-section.elementor-element.elementor-section-boxed.elementor-section-height-default.elementor-section-height-default > div > div > div > div > div > div > div > div div div.jet-woo-categories-content div h5 a::attr(href)").getall()
        
        
        '''car_mark_list = response.css("#main > div > div > section.elementor-section.elementor-top-section.elementor-element.elementor-section-boxed.elementor-section-height-default.elementor-section-height-default > div > div > div > div > div > div > div > div")
        
        for car_mark in car_mark_list:
            car_model_page_url = car_mark.css("div div.jet-woo-categories-content div h5 a::attr(href)").get()
            car_mark_name = car_mark.css("div div.jet-woo-categories-content div h5 a::text").get()'''
            
        for car_mark_url in car_mark_urls:
            
            yield response.follow(car_mark_url, callback = self.parse_model_page,
                                  )
            
    def parse_model_page(self, response):
        car_model_urls = response.css("#main > div > div > section > div > div > div > div.elementor-element.elementor-widget.elementor-widget-jet-woo-categories > div > div > div > div div div.jet-woo-categories-content div h5 a::attr(href)").getall()
        car_models = response.css(".jet-woo-categories-content .jet-woo-categories-title__wrap h5 a::text").getall()
        '''car_model_list = response.css("#main > div > div > section > div > div > div > div.elementor-element.elementor-widget.elementor-widget-jet-woo-categories > div > div > div > div")

        for car_model in car_model_list:
            car_parts_page_url = car_model.css("div div.jet-woo-categories-content div h5 a::attr(href)").get()
            car_model_name = car_model.css("div div.jet-woo-categories-content div h5 a::text").get()'''
            
        for i, car_model_url in enumerate(car_model_urls):

            yield response.follow(car_model_url, callback = self.parse_part_page_initial,
                                  meta = {"car_model": car_models[i], "car_model_url": car_model_url}
                                  )

    def parse_part_page_initial(self, response):
        car_mark = response.css("nav.woocommerce-breadcrumb a:nth-of-type(2)::text").get()
        car_model = response.meta["car_model"]
        scraped_page_numbers = ["1"]
        
        part_list = response.css("div.elementor-jet-woo-builder-products-loop .jet-woo-products-wrapper ul.products li")
        
        for part in part_list:
            item = NawilebiItem()
            item["website"] = "https://megaautoparts.ge/"
            item["car_mark"] = car_mark
            item["car_model"] = response.meta["car_model"]
            item["part_url"] = part.css("div div section div.elementor-container div div div:nth-of-type(1) div div div a::attr(href)").get()
            item["part_full_name"] = part.css("div div section div.elementor-container div div div:nth-of-type(2) div h5 a::text").get()
            price = part.css("div div section div.elementor-container div div div:nth-of-type(3) div div div")
            if price.css("del") or price.css("ins"):
                item["price"] = price.css("ins span bdi::text").get()
                item["original_price"] = price.css("del span bdi::text").get()
            else:
                item["price"] = part.css("span bdi::text").get()
                
            item["start_year"]= None
            item["end_year"] = None
            item["year"] = None
            
            yield item
        
        
        nav_list = response.css("nav.jet-woo-builder-shop-pagination a")
        if nav_list:
            for nav in nav_list:
                if nav:
                    next_page_number = nav.css("::text").get()
                    if next_page_number not in scraped_page_numbers:
                        scraped_page_numbers.append(next_page_number)
                        yield response.follow(f"https://megaautoparts.ge/product-category/{car_mark.lower()}/{self.adjust_car_name_for_url_megaauto(response.meta['car_model'])}/page/{next_page_number}/", callback = self.parse_next_page,
                                      meta = {"car_mark": car_mark, "car_model": car_model, "scraped_page_numbers": scraped_page_numbers})
                        
                        
    def parse_next_page(self, response):
        car_mark = response.meta["car_mark"]
        car_model = response.meta["car_model"]
        scraped_page_numbers = response.meta["scraped_page_numbers"]
        
        part_list = response.css("div.elementor-jet-woo-builder-products-loop .jet-woo-products-wrapper ul.products li")
        
        for part in part_list:
            item = NawilebiItem()
            item["website"] = "https://megaautoparts.ge/"
            item["car_mark"] = response.meta["car_mark"]
            item["car_model"] = response.meta["car_model"]
            item["part_url"] = part.css("div div section div.elementor-container div div div:nth-of-type(1) div div div a::attr(href)").get()
            item["part_full_name"] = part.css("div div section div.elementor-container div div div:nth-of-type(2) div h5 a::text").get()
            price = part.css("div div section div.elementor-container div div div:nth-of-type(3) div div div")
            if price.css("del") or price.css("ins"):
                item["price"] = price.css("ins span bdi::text").get()
                item["original_price"] = price.css("del span bdi::text").get()
            else:
                item["price"] = part.css("span bdi::text").get()
                
            item["start_year"]= None
            item["end_year"] = None
            item["year"] = None
            
            yield item
        
        
        nav_list = response.css("nav.jet-woo-builder-shop-pagination a")
        if nav_list:
            for nav in nav_list:
                if nav:
                    next_page_number = nav.css("::text").get()
                    if next_page_number not in scraped_page_numbers:
                        scraped_page_numbers.append(next_page_number)
                        yield response.follow(f"https://megaautoparts.ge/product-category/{car_mark.lower()}/{self.adjust_car_name_for_url_megaauto(response.meta['car_model'])}/page/{next_page_number}/", callback = self.parse_next_page,
                                      meta = {"car_mark": car_mark, "car_model": car_model, "scraped_page_numbers": scraped_page_numbers})