import scrapy
from nawilebi.items import NawilebiItem

class ZupartsSpider(scrapy.Spider):
    name = "zuparts"
    allowed_domains = ["zupart.ge", "proxy.scrapeops.io"]
    start_urls = ["https://zupart.ge/ka"]
    custom_settings = {
        'ITEM_PIPELINES': {
            "nawilebi.pipelines.NawilebiPipeline": 100,
            "nawilebi.pipelines.ZupartsPipeline": 200,
            "nawilebi.pipelines.SaveToMySQLPipeline": 900
        },
        'DOWNLOAD_DELAY': 5,
        'SCRAPEOPS_PROXY_ENABLED': True,
        "DOWNLOADER_MIDDLEWARES":{
            #'scrapeops_scrapy.middleware.retry.RetryMiddleware': 550,
           # 'scrapy.downloadermiddlewares.retry.RetryMiddleware': None,
            "nawilebi.middlewares.FakeBrowserHeaderAgentMiddleware": 101,
            "scrapeops_scrapy_proxy_sdk.scrapeops_scrapy_proxy_sdk.ScrapeOpsScrapyProxySdk": 100
        }
    }
    
    
    def parse(self, response):
        car_mark_list = response.css("body > main > ul > li")
        
        for car_mark in car_mark_list:
            car_model_page_url = car_mark.css("a::attr(href)").get()
            car_mark_name = car_mark.css("a h2::text").get().upper()
            
            yield response.follow(car_model_page_url, callback = self.parse_model_page,
                                  meta = {"car_mark": car_mark_name})
            
    def parse_model_page(self, response):
        car_model_list = response.css("#contentAjax > ul > li")
        
        for car_model in car_model_list:
            part_page_url = car_model.css("a::attr(href)").get()
            car_model_name = car_model.css("a h2::text").get().upper()
            
            yield response.follow(part_page_url, callback = self.parse_part_list,
                                  meta = {"car_mark": response.meta["car_mark"], "car_model": car_model_name})
            
    def parse_part_list(self, response):
        part_list = response.css("body > main > div.products-insider-div > section > ul > li")
        
        
        
        for part in part_list:
            item = NawilebiItem()
            item["part_url"] = part.css("div.prod-main-wrapper div.prod-info-wrap a::attr(href)").get()
            item["price"] = part.css("div.prod-main-wrapper div.prod-info-wrap p .current-price::text").get()
            item["website"] = "https://zupart.ge/ka"
            item["car_mark"] = response.meta["car_mark"]
            item["car_model"] = response.meta["car_model"]
            item["part_full_name"] = part.css("div.prod-main-wrapper div.prod-info-wrap a h2::text").get().strip()
            item["year"] = None
            item["start_year"] = None
            item["end_year"] = None
            
            yield item