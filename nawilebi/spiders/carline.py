import scrapy
from nawilebi.items import NawilebiItem

class CarlineSpider(scrapy.Spider):
    name = "carline"
    allowed_domains = ["carline.ge"]
    start_urls = ["https://carline.ge/"]
    custom_settings = {
            'ITEM_PIPELINES': {
            "nawilebi.pipelines.NawilebiPipeline": 300,
            "nawilebi.pipelines.CarlinePipeline": 200,
            #"nawilebi.pipelines.YearProcessPipeline": 300,
            "nawilebi.pipelines.SaveToMySQLPipeline": 900
        },
        #'DOWNLOAD_DELAY': 0.5,
    }
    avoid_urls = [
        "https://carline.ge/catalog/product/shekvethith/"
    ]
    
    def parse(self, response):
        car_mark_list = response.css("#categories > div")
        
        for car_mark in car_mark_list:
            car_model_url = car_mark.css("div div.cascade_title h4 a::attr(href)").get()
            car_mark_name = car_mark.css("div div.cascade_title h4 a::text").get()
            
            if car_mark_name == "KIA":
                yield response.follow("https://carline.ge/catalog/kia/", callback = self.parse_part_page,
                                  meta = {"car_mark": car_mark_name})
            else:
                yield response.follow(car_model_url, callback = self.parse_model_page,
                                  meta = {"car_mark": car_mark_name})
            
    def parse_model_page(self, response):
        car_model_list = response.css("#categories > div")
        
        for car_model in car_model_list:
            part_page_url = car_model.css("div .cascade_title h4 a::attr(href)").get()
            car_model_name = car_model.css("div .cascade_title h4 a::text").get()
            
            yield response.follow(part_page_url, callback = self.parse_part_page,
                                  meta = {"car_mark": response.meta["car_mark"], "car_model": car_model_name})
            
    def parse_part_page(self, response):
        part_list = response.css("#items > div")
        item = NawilebiItem()
        
        for part in part_list:
            part_url = part.css("div .cascade_title h4 a::attr(href)").get()
            
            if part_url in self.avoid_urls:
                self.logger.info(f"Skipping URL: {part_url}")
                continue
                
            item["part_url"] = part_url
            item["part_full_name"] = part.css("div .cascade_title h4 a::text").get()
            item["part_url"] = part.css("div .cascade_title h4 a::attr(href)").get()
            item["in_stock"] = part.css("div .avail strong::text").get()
            item["price"] = part.css("div .price span::text").get()
            item["website"] = "https://carline.ge/"
            item["car_mark"] = response.meta["car_mark"]
            if "car_model" in response.meta:
                item["car_model"] = response.meta["car_model"]
            else: item["car_model"] = None
            item["year"] = None
            
            yield item 
            
        