import scrapy
from nawilebi.items import NawilebiItem

class SoloautoSpider(scrapy.Spider):
    name = "soloauto"
    allowed_domains = ["soloauto.ge", "proxy.scrapeops.io"]
    start_urls = ["https://soloauto.ge/"]
    custom_settings = {
        'ITEM_PIPELINES': {
            "nawilebi.pipelines.NawilebiPipeline": 300,
            "nawilebi.pipelines.SoloautoPipeline": 200,
            "nawilebi.pipelines.SoloautoPipeline_2": 201,
            "nawilebi.pipelines.SaveToMySQLPipeline": 900
        },
        #'DOWNLOAD_DELAY': 3,
        'SCRAPEOPS_PROXY_ENABLED': True,
        "DOWNLOADER_MIDDLEWARES":{
            #'scrapeops_scrapy.middleware.retry.RetryMiddleware': 550,
            #'scrapy.downloadermiddlewares.retry.RetryMiddleware': None,
            "nawilebi.middlewares.FakeBrowserHeaderAgentMiddleware": 101,
            "scrapeops_scrapy_proxy_sdk.scrapeops_scrapy_proxy_sdk.ScrapeOpsScrapyProxySdk": 100
        }
    }
    
    
    def parse(self, response):
       car_mark_list = a = response.css("#content > div.page-content > div > section > div > div> div > div > div")
       
       for car_mark in car_mark_list:
           car_mark_url = car_mark.css("a::attr(href)").get()
           
           if car_mark_url:
               
               yield response.follow(car_mark_url, callback = self.parse_mark_page)
               
    def parse_mark_page(self, response):
        car_model_list = response.css("#content > div.page-content > div > section > div > div > div > div > div > div > ul li")
        car_mark = response.css(".woocommerce-breadcrumb::text").get().strip()
        
        for car_model in car_model_list:
            part_list_url = car_model.css("a::attr(href)").get()
            car_model_name = car_model.css("a h2::text").get().strip()
            
            if part_list_url:
                
                yield response.follow(part_list_url, callback = self.parse_part_list,
                                      meta = {"car_mark": car_mark, "car_model": car_model_name})
    
    def parse_part_list(self, response):
        part_list = response.css("body > div.elementor > section > div > div > div > div > div > div > ul li")
        car_mark= response.css("nav.woocommerce-breadcrumb ")
        
        for part in part_list:
            item = NawilebiItem()
            item["car_mark"] = response.meta["car_mark"]
            item["car_model"] = response.meta["car_model"]
            item["website"] = "https://soloauto.ge/"
            item["part_url"] = part.css("a:nth-of-type(1)::attr(href)").get()
            item["part_full_name"] = part.css("a:nth-of-type(1) h2::text").get()
            item["price"] = part.css("a:nth-of-type(1) span span bdi::text").get()
            
            yield item
            
    '''def parse_part_list(self, response):
        part_list = response.css("body > div.elementor > section > div > div > div > div > div > div > ul li")
        
        for part in part_list:
            part_url = part.css("a:nth-of-type(1)::attr(href)").get()
            
            if part_url:
                
                yield response.follow(part_url, callback = self.parse_part_page)
                
    def parse_part_page(self, response):
        item = NawilebiItem()
        
        item["car_mark"] = response.css("body > div > section > div > div > div > div > div > nav > a:nth-child(2)::text").get().strip()
        item["car_model"] = response.css("body > div > section > div > div > div > div > div > nav > a:nth-child(3)::text").get().strip()
        item["part_url"] = response.url
        item["website"] = "https://soloauto.ge/"
        item["part_full_name"] = response.css("div > section > div > div > div > section > div > div > div > div > div > div > div > h4::text").get().strip()
        item["price"] = response.css("div > section > div > div > div > section > div > div > div > div > div > div > div > p > span > bdi::text").get().strip()
        item["in_stock"] = True if response.css(".elementor-add-to-cart p::text").get().strip()  == "მარაგში" else False
        item["year"] = None
        item["start_year"] = None
        item["end_year"] = None
        
        yield item'''