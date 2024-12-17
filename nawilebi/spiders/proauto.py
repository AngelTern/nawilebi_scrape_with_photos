import scrapy
from nawilebi.items import NawilebiItem

class ProautoSpider(scrapy.Spider):
    name = "proauto"
    allowed_domains = ["pro-auto.ge"]
    start_urls = ["https://pro-auto.ge/ka/products/marks"]
    custom_settings = {
        'ITEM_PIPELINES': {
            "nawilebi.pipelines.NawilebiPipeline": 300,
            "nawilebi.pipelines.ProautoPipeline": 200,
            #"nawilebi.pipelines.YearProcessPipeline": 300,
            "nawilebi.pipelines.SaveToMySQLPipeline": 900
        },
        #'DOWNLOAD_DELAY': 0.5,
    }
    
    
    
    
    def parse(self, response):
        car_mark_list = response.css("body > main > section > div > div > div > div > div > div")
        
        for car_mark in car_mark_list:
            car_model_url = car_mark.css("a::attr(href)").get()
            car_mark_name = car_mark.css("a h3::text").get().upper()
            
            yield response.follow(car_model_url, callback=self.parse_model_page,
                                  meta={"car_mark": car_mark_name})
            
    def parse_model_page(self, response):
        car_model_list = response.css("body > main > section > div > div > div.col-lg-9 > div > div > div")
        
        for car_model in car_model_list:
            part_page_url = car_model.css("a::attr(href)").get()
            car_model_name = car_model.css("a h3::text").get()
            year = car_model.css("a p::text").get()
            
            yield response.follow(part_page_url, callback=self.parse_part_page,
                                  meta={"car_mark": response.meta["car_mark"], "car_model": car_model_name,
                                        "year": year})
            
    def parse_part_page(self, response):
        part_list = response.css("body > main > section > div > div > div.col-lg-9 > div.products-list-inner > div > div")
        
        for part in part_list:
            item = NawilebiItem()
            item["part_url"] = part.css("div div.latest-car-content-wrap div.latest-car-content h3 a::attr(href)").get()
            item["part_full_name"] = part.css("div div.latest-car-content-wrap div.latest-car-content h3 a::text").get()
            item["in_stock"] = True if part.css("div div.latest-car-content-wrap div.latest-car-bottom ul p::text").get() == "მარაგშია" else False
            item["car_model"] = response.meta["car_model"]
            item["car_mark"] = response.meta["car_mark"]
            item["year"] = response.meta["year"]
            item["website"] = "https://pro-auto.ge/"
            item['start_year'] = None
            item["end_year"] = None
            price_span = part.css("div div.latest-car-content-wrap div.latest-car-bottom ul li span.price")
            
            if price_span.css("del"):
                item["original_price"] = price_span.css("del::text").get()
                item["price"] = price_span.css("::text").get()
            else:
                item["price"] = price_span.css("::text").get()
            
            yield item
        
        navigation_list = response.css("body > main > section > div > div > div.col-lg-9 > div.row > div > div > div > div > nav > ul li")
        navigation_list = navigation_list[1:-1]
        
        for navigation in navigation_list:
            if "active" not in navigation.css("::attr(class)").get():
                next_page_url = navigation.css("a::attr(href)").get()
                
                yield response.follow(next_page_url, callback=self.parse_next_page,
                                      meta={"car_mark": response.meta["car_mark"], "car_model": response.meta["car_model"],
                                            "year": response.meta["year"]})
            
    def parse_next_page(self, response):
        part_list = response.css("body > main > section > div > div > div.col-lg-9 > div.products-list-inner > div > div")
        
        for part in part_list:
            item = NawilebiItem()
            item["part_url"] = part.css("div div.latest-car-content-wrap div.latest-car-content h3 a::attr(href)").get()
            item["part_full_name"] = part.css("div div.latest-car-content-wrap div.latest-car-content h3 a::text").get()
            item["in_stock"] = True if part.css("div div.latest-car-content-wrap div.latest-car-bottom ul p::text").get() == "მარაგშია" else False
            item["car_model"] = response.meta["car_model"]
            item["car_mark"] = response.meta["car_mark"]
            item["year"] = response.meta["year"] 
            item["website"] = "https://pro-auto.ge/"
            item['start_year'] = None
            item["end_year"] = None
            price_span = part.css("div div.latest-car-content-wrap div.latest-car-bottom ul li span.price")
            
            if price_span.css("del"):
                item["original_price"] = price_span.css("del::text").get()
                item["price"] = price_span.css("::text").get()
            else:
                item["price"] = price_span.css("::text").get()
            
            yield item
