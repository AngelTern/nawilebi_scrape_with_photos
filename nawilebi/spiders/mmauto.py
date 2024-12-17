import scrapy
from nawilebi.items import NawilebiItem
import re
#from nawilebi.utilities.additional_functions import extract_id_mmauto

class MmautoSpider(scrapy.Spider):
    name = "mmauto"
    allowed_domains = ["mmauto.ge"]
    start_urls = ["https://mmauto.ge/"]
    custom_settings = {
        'ITEM_PIPELINES': {
            "nawilebi.pipelines.NawilebiPipeline": 300,
            "nawilebi.pipelines.MmautoPipeline": 200,
            #"nawilebi.pipelines.YearProcessPipeline": 300,
            "nawilebi.pipelines.SaveToMySQLPipeline": 900
        },
        #'DOWNLOAD_DELAY': 0.5,
    }
    
    def extract_id_mmauto(self, url):
        match = re.search(r'/vehicle/(\d+)/', url)
        if match:
            vehicle_id = match.group(1)
            return vehicle_id
        else: return None
    
    def parse(self, response):
        car_mark_list = response.css("body > div.container.py-3 > div.row > div")
        
        for car_mark in car_mark_list:
            mark_url = car_mark.css("div a::attr(href)").get()
            mark_name = car_mark.css("div a div h1::text").get()
            
            yield response.follow(mark_url, callback = self.parse_mark_page,
                                  meta = {'car_mark': mark_name})
            
    def parse_mark_page(self, response):
        model_list = response.css("body > div.container > div.row > div")
        
        for model in model_list:
            model_url = model.css("div a::attr(href)").get()
            model_name = model.css("div a h6::text").get()
            
            
            yield response.follow(model_url, callback = self.parse_part_list,
                                  meta = {"car_mark": response.meta["car_mark"], "car_model": model_name})
            
    def parse_part_list(self, response):
        model_id = self.extract_id_mmauto(response.url)
        
        part_list = response.css("#rows > div")
        model_name = response.css("body > div.bg-secondary.text-white > div > h1::text").get()
        
        for part in part_list:
            item = NawilebiItem()
            item["part_url"] = "https://mmauto.ge/" + part.css("div a::attr(href)").get()
            item["part_full_name"] = part.css("div a h6::text").get()
            item["price"] = part.css(".text-secondary.text-center::text").get()
            item["in_stock"] = part.css("div a div.text-center span:nth-of-type(1) ::text").getall()
        
            '''if in_stock.strip() == "მარაგშია":
                item["in_stock"] = True
            else:
                item["in_stock"] = False'''
            item["car_mark"] = response.meta["car_mark"]
            item["car_model"] = model_name
            item["year"] = None
            item["start_year"] = None
            item["end_year"] = None
            item["website"] = "https://mmauto.ge/"
            
            yield item
            
        if len(part_list) == 12:
            page_number = 1
            yield response.follow(f"https://mmauto.ge//vehicle/{model_id}/ajax?page={page_number}&vehicle_id={model_id}&name=", callback = self.parse_ajax,
                                  meta = {"car_mark": response.meta["car_mark"], "car_model": model_name, "page_number": page_number, "model_id": model_id})
            
    def parse_ajax(self, response):
        part_list = response.css("body > div")
        if len(part_list) > 0:
            for part in part_list:
                item = NawilebiItem()
                item["part_url"] = "https://mmauto.ge/" + part.css("div a::attr(href)").get()
                item["part_full_name"] = part.css("div a h6::text").get()
                item["price"] = part.css(".text-secondary.text-center::text").get()
                item["in_stock"] = part.css(".text-center span:nth-of-type(1)::text").getall()
            
                '''if in_stock.strip() == "მარაგშია":
                    item["in_stock"] = True
                else:
                    item["in_stock"] = False'''
                item["car_mark"] = response.meta["car_mark"]
                item["car_model"] = response.meta["car_model"]
                item["year"] = None
                item["start_year"] = None
                item["end_year"] = None
                item["website"] = "https://mmauto.ge/"
                
                yield item
            page_number = response.meta["page_number"] + 1
            model_id = model_id = response.meta['model_id']
            yield response.follow(f"https://mmauto.ge//vehicle/{model_id}/ajax?page={page_number}&vehicle_id={model_id}&name=", callback = self.parse_ajax,
                                  meta = {"car_mark": response.meta["car_mark"], "car_model": response.meta["car_model"], "page_number": page_number, "model_id": model_id})
                
            
