import scrapy
#from nawilebi.utilities.additional_functions import adjust_car_model_name_carparts
from nawilebi.items import NawilebiItem

class CarpartsSpider(scrapy.Spider):
    name = "carparts"
    allowed_domains = ["car-parts.ge", "proxy.scrapeops.io"]
    start_urls = ["https://car-parts.ge"]
    custom_settings = {
        'ITEM_PIPELINES': {
            "nawilebi.pipelines.NawilebiPipeline": 300,
            "nawilebi.pipelines.CarpartsPipeline": 200,
            #"nawilebi.pipelines.YearProcessPipeline": 300,
            "nawilebi.pipelines.SaveToMySQLPipeline": 900
        },
        #'DOWNLOAD_DELAY': 0.5,
        'SCRAPEOPS_PROXY_ENABLED': True,
        "DOWNLOADER_MIDDLEWARES":{
            #'scrapeops_scrapy.middleware.retry.RetryMiddleware': 550,
            #'scrapy.downloadermiddlewares.retry.RetryMiddleware': None,
            "nawilebi.middlewares.FakeBrowserHeaderAgentMiddleware": 101,
            "scrapeops_scrapy_proxy_sdk.scrapeops_scrapy_proxy_sdk.ScrapeOpsScrapyProxySdk": 100
        }
    }
    
    def adjust_car_model_name_carparts(self, car_model):
        car_model_lowered = car_model.lower()
        car_model_adjusted = car_model_lowered.replace(" ", "-")
        return car_model_adjusted
    def parse(self, response):
        car_marks_list = response.css(".view-content > div")
        for car_mark in car_marks_list:
            relative_url = car_mark.css(".shop-item div.details p a::attr(href)").get()
            car_mark = car_mark.css(".shop-item div.details p a::text").get()
            car_mark_url = response.url + relative_url
            
            yield response.follow(car_mark_url, callback = self.parse_car_mark,
                                  meta = {"car_mark": car_mark})
            
    def parse_car_mark(self, response):
        car_model_list = response.css(".view-content > div")
        car_mark = response.meta["car_mark"]
        
        for car_model in car_model_list:
            relative_url = car_model.css(".shop-item .details p a::attr(href)").get()
            car_model_url = "https://car-parts.ge" + relative_url 
            car_model_name = car_model.css(".shop-item .details p a::text").get()
            car_model_name_adjusted = self.adjust_car_model_name_carparts(car_model_name)
            car_model_url_pagination = f"https://car-parts.ge/ka/produqcia/{car_model_name_adjusted}?page="
            
            yield response.follow(car_model_url, callback = self.parse_car_model,
                                  meta = {"car_model": car_model_name, "car_mark": car_mark, "car_model_url_pagination": car_model_url_pagination,
                                          "car_model_name_adjusted": car_model_name_adjusted})
            
            

    def parse_car_model(self, response):
        pagination = response.css("div.item-list ul > li")
        if len(pagination) != 0:
            for i in pagination:
                if i.css("a::attr(href)"):
                    yield response.follow(i.css("a::attr(href)").get(), callback = self.parse_part_list,
                                        meta = {"car_mark": response.meta["car_mark"], "car_model": response.meta["car_model"]})
                    
    def parse_part_list(self, response):
        part_list = response.css("div.shop-listing > div")
        
        for part in part_list:
            item = NawilebiItem()
            
            item["car_mark"] = response.meta["car_mark"]
            item["car_model"] = response.meta["car_model"]
            item["website"] = "https://car-parts.ge"
            item["part_url"] = "https://car-parts.ge" + part.css("div div.details p:nth-of-type(1) a::attr(href)").get()
            item["part_full_name"] = part.css("div div.details p:nth-of-type(1) a::text").get()
            item["price"] = part.css("div div.details p:nth-of-type(2)::text").get()
            item["year"] = None
            item["start_year"] = None
            item["end_year"] = None
            
            yield item
        
    '''def parse_car_model(self, response):
        pagination = response.css("div.item-list ul > li")
               
        
        if len(pagination) != 0:
            num_of_pages = len(pagination) - 2
            for i in range(num_of_pages):
                yield response.follow(response.meta["car_model_url_pagination"] + str(i), callback = self.parse_part_page_pagination,
                                      meta = {"car_mark": response.meta["car_mark"], "car_model": response.meta["car_model"]})
        else:
            part_list = response.css("div.shop-listing > div")
            
            for part in part_list:
                relative_url = part.css("div div.details p:nth-of-type(1) a::attr(href)").get()
                part_url = "https://car-parts.ge" + relative_url
                yield response.follow(part_url, self.parse_part_page,
                                      meta = {"car_mark": response.meta["car_mark"], "car_model": response.meta["car_model"]})
                
                
    
    def parse_part_page_pagination(self, response):
        part_list = response.css("div.shop-listing > div")
            
        for part in part_list:
            relative_url = part.css("div div.details p:nth-of-type(1) a::attr(href)").get()
            part_url = "https://car-parts.ge" + relative_url
            yield response.follow(part_url, self.parse_part_page,
                                  meta = {"car_mark": response.meta["car_mark"], "car_model": response.meta["car_model"]})
            
    def parse_part_page(self, response):
        item = NawilebiItem()   
        
        item["website"] = "https://car-parts.ge"
        item["part_url"] = response.url
        item["car_mark"] = response.meta["car_mark"]
        item["part_full_name"] = response.css("#riva-site-wrapper > div.container > div > div.col-xs-12.col-sm-8.col-lg-9 > section > div.row > div.col-xs-12.col-sm-8.col-lg-7 > p.product-title::text").get()
        item["in_stock"] = response.css("#riva-site-wrapper > div.container > div > div.col-xs-12.col-sm-8.col-lg-9 > section > div.row > div.col-xs-12.col-sm-8.col-lg-7 > div.field.field-name-field-quantity.field-type-list-text.field-label-inline.clearfix > div.field-items > div::text").get()
        item["car_model"] = response.meta["car_model"]
        year = response.css("#riva-site-wrapper > div.container > div > div.col-xs-12.col-sm-8.col-lg-9 > section > div.row > div.col-xs-12.col-sm-8.col-lg-7 > div.field.field-name-field-year.field-type-text.field-label-inline.clearfix > div.field-items > div::text").get()
        if year:
            item["year"] = year
        
        item["price"] = response.css("#price_id::text").get()
        item["start_year"] = None
        item["end_year"] = None
        
        yield item'''
        