import scrapy
import re
from nawilebi.items import NawilebiItem

class ApgpartsSpider(scrapy.Spider):
    name = "apgparts"
    allowed_domains = ["apgparts.ge", "proxy.scrapeops.io"]
    start_urls = ["https://apgparts.ge/brand/toyota/", "https://apgparts.ge/brand/hyundai/", "https://apgparts.ge/brand/mazda/"]
    main_domain = "https://apgparts.ge/"
    custom_settings = {
    'ITEM_PIPELINES': {
        "nawilebi.pipelines.NawilebiPipeline": 300,
        "nawilebi.pipelines.ApgpartsPipeline": 200,
        "nawilebi.pipelines.SaveToMySQLPipeline": 900
    },
    'SCRAPEOPS_API_KEY': '606557b4-c18b-42c7-b503-988adcc0a99a',  # Updated API key
    'SCRAPEOPS_PROXY_ENABLED': True,
    'DOWNLOADER_MIDDLEWARES': {
        "nawilebi.middlewares.FakeBrowserHeaderAgentMiddleware": 101,
        "scrapeops_scrapy_proxy_sdk.scrapeops_scrapy_proxy_sdk.ScrapeOpsScrapyProxySdk": 100,
    }
}

    
    
    def parse(self, response):
        car_model_columns = response.css("body > div.website-wrapper > div.main-page-wrapper > div.container > div > div > div.term-description > div > section > div > div")
        
        for column in car_model_columns:
            inner_car_marks = column.css("div > div.elementor-element")
            for car_mark in inner_car_marks:
                uncleaned_relative_url = car_mark.css("div div div::attr(onclick)").get()
                uncleaned_relative_url_1 = re.sub("window.location.href=", '', uncleaned_relative_url)
                relative_url = re.sub("'", '', uncleaned_relative_url_1)
                
                yield response.follow(self.main_domain + relative_url, callback = self.parse_model_page)
                
    def parse_model_page(self, response):
        part_list = response.css("body > div.website-wrapper > div.main-page-wrapper > div.container > div > div > div.products > div")
        
        for part in part_list:
            item = NawilebiItem()
            item["website"] = "https://apgparts.ge/"
            item["part_url"] = part.css("div div:nth-of-type(1) a.product-image-link::attr(href)").get()
            item["part_full_name"] = part.css("div div:nth-of-type(2) h3 a::text").get()
            item["price"] = part.css("div div:nth-of-type(2) span.price span bdi::text").get()
            item["car_model"] = response.css("body > div.website-wrapper > div.main-page-wrapper > div.page-title > div > h1::text").get()
            item["car_mark"] = None
            item["start_year"] = None
            item["end_year"] = None
            item["year"] = None
            
            yield item
            
        navigation_list = response.css("body > div.website-wrapper > div.main-page-wrapper > div.container > div > div > div.wd-loop-footer.products-footer > nav > ul > li")
        if navigation_list:
            for nav in navigation_list:
                if nav.css("span") or nav.css("a::attr(class)").get() == "next":
                    continue
                else:  
                    next_page_url = nav.css("a::attr(href)").get()
                    
                    yield response.follow(next_page_url, callback=self.parse_next_page)
                
    def parse_next_page(self, response):
        part_list = response.css("body > div.website-wrapper > div.main-page-wrapper > div.container > div > div > div.products > div")
        
        for part in part_list:
            item = NawilebiItem()
            item["website"] = "https://apgparts.ge/"
            item["part_url"] = part.css("div div:nth-of-type(1) a.product-image-link::attr(href)").get()
            item["part_full_name"] = part.css("div div:nth-of-type(2) h3 a::text").get()
            item["price"] = part.css("div div:nth-of-type(2) span.price span bdi::text").get()
            item["car_model"] = response.css("body > div.website-wrapper > div.main-page-wrapper > div.page-title > div > h1::text").get()
            item["car_mark"] = None
            item["start_year"] = None
            item["end_year"] = None
            item["year"] = None
            
            yield item
            