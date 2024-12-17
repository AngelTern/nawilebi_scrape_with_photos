import scrapy
from nawilebi.items import NawilebiItem
import re

class NewpartsSpider(scrapy.Spider):
    name = "newparts"
    allowed_domains = ["newparts.ge"]
    start_urls = ["https://newparts.ge/"]
    custom_settings = {
        'ITEM_PIPELINES': {
            "nawilebi.pipelines.NawilebiPipeline": 300,
            "nawilebi.pipelines.NewpartsPipeline": 200,
            #"nawilebi.pipelines.YearProcessPipeline": 300,
            "nawilebi.pipelines.SaveToMySQLPipeline": 900
        },
        #'DOWNLOAD_DELAY': 0.5,
    }
    
    def parse(self, response):
        car_mark_list = response.css("body > div.container.mt-4 > div > div")
        
        for car_mark in car_mark_list:
            relative_url = car_mark.css("div a::attr(href)").get()
            car_mark_name = car_mark.css("div a div img::attr(alt)").get().upper()
            
            yield response.follow(self.start_urls[0] + relative_url, callback=self.parse_model_page,
                                  meta={"car_mark": car_mark_name})
            
    def parse_model_page(self, response):
        car_model_list = response.css("body > div.container.py-4 > div > div")
        
        for car_model in car_model_list:
            relative_url = car_model.css("div a::attr(href)").get()
            car_model_name = car_model.css("div a h6.dark-love::text").get()
            year = car_model.css("div a div div.years span::text").get()
            
            yield response.follow(self.start_urls[0] + relative_url, callback=self.parse_part_list,
                                  meta={"car_mark": response.meta["car_mark"], "car_model": car_model_name, "year": year})
            
    def parse_part_list(self, response):
        part_list = response.css("#rows > div")
        
        for part in part_list:
            item = NawilebiItem()
            item["website"] = "https://newparts.ge/"
            item["car_mark"] = response.meta["car_mark"]
            item["car_model"] = response.meta["car_model"]
            item["year"] = response.meta["year"]
            item["start_year"] = None
            item["end_year"] = None
            item["part_url"] = self.start_urls[0] + part.css("div a::attr(href)").get()
            item["part_full_name"] = part.css("div a div:nth-of-type(2) h6 span.me-1::text").get() + part.css("div a div:nth-of-type(2) h6 span.badge::text").get() if part.css("div a div:nth-of-type(2) h6 span.badge::text").get() else part.css("div a div:nth-of-type(2) h6 span.me-1::text").get()
            item["price"] = part.css("div a div:nth-of-type(2) small::text").get()
            not_in_stock = part.css("div a div:nth-of-type(1) div.stock")
            item["in_stock"] = False if not_in_stock else True

            yield item

        id_pattern = r'/vehicle/(\d+)/'
        match = re.search(id_pattern, response.url)
        if match:
            number = match.group(1)
            page_number = 1
            yield response.follow(f"https://newparts.ge/vehicle/{number}/ajax?page={page_number}&vehicle_id={number}&name=", callback=self.parse_part_api,
                                  meta={"car_mark": response.meta["car_mark"], "car_model": response.meta["car_model"], "year": response.meta["year"], 
                                        "page_number": page_number, "number": number})
            
    def parse_part_api(self, response):
        part_list = response.css("body > div")
        
        if part_list:
            for part in part_list:
                item = NawilebiItem()
                item["website"] = "https://newparts.ge/"
                item["car_mark"] = response.meta["car_mark"]
                item["car_model"] = response.meta["car_model"]
                item["year"] = response.meta["year"]
                item["start_year"] = None
                item["end_year"] = None
                item["part_url"] = self.start_urls[0] + part.css("div a::attr(href)").get()
                #item["part_full_name"] = part.css("div a div:nth-of-type(2) h6 span.me-1::text").get() + part.css("div a div:nth-of-type(2) h6 span.badge::text").get() if part.css("div a div:nth-of-type(2) h6 span.badge::text").get() else part.css("div a div:nth-of-type(2) h6 span.me-1::text").get()
                part_name_1 = part.css("div a div:nth-of-type(2) h6 span.me-1::text").get()
                part_name_2 = part.css("div a div:nth-of-type(2) h6 span.badge::text").get()
                if part_name_1 and part_name_2:
                    item["part_full_name"] = part_name_1 + " " + part_name_2
                else:
                    item["part_full_name"] = part_name_1 if part_name_1 else part_name_2
                
                item["price"] = part.css("div a div:nth-of-type(2) small::text").get()
                not_in_stock = part.css("div a div:nth-of-type(1) div.stock")
                item["in_stock"] = False if not_in_stock else True

                yield item

            page_number = response.meta["page_number"] + 1
            number = response.meta["number"]
            
            yield response.follow(f"https://newparts.ge/vehicle/{number}/ajax?page={page_number}&vehicle_id={number}&name=", callback=self.parse_part_api,
                                  meta={"car_mark": response.meta["car_mark"], "car_model": response.meta["car_model"], "year": response.meta["year"],
                                        "page_number": page_number, "number": number})
        else:
            self.logger.info("No more parts found.")
