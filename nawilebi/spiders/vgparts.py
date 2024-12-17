import scrapy
from nawilebi.items import NawilebiItem
#from nawilebi.utilities.additional_functions import get_digits_after_last_slash
import json

class VgpartsSpider(scrapy.Spider):
    name = "vgparts"
    allowed_domains = ["vgparts.ge"]
    start_urls = ["https://vgparts.ge/api/product/manufacturer/0"]
    custom_settings = {
        'ITEM_PIPELINES': {
            "nawilebi.pipelines.NawilebiPipeline": 300,
            "nawilebi.pipelines.VgpartsPipeline": 200,
            #"nawilebi.pipelines.YearProcessPipeline": 300,
            "nawilebi.pipelines.SaveToMySQLPipeline": 900
        },
        #'DOWNLOAD_DELAY': 0.5,
    }
    
    def get_digits_after_last_slash(string):
        match = re.search(r"/(\d+)(?=[^/]*$)", string)
        if match:
            return match.group(1)
        return None
    
    def parse(self, response):
        json_data = json.loads(response.text)
        
        for item in json_data["result"]:
            car_mark_id = item.get("id")
            car_mark = item.get("name")
            yield response.follow("https://vgparts.ge/api/product/manufacturer/" + str(car_mark_id), callback = self.parse_car_mark,
                                  meta = {"car_mark": car_mark})
            
    def parse_car_mark(self, response):
        json_data = json.loads(response.text)
        car_mark = response.meta["car_mark"]
        
        for item in json_data["result"]:
            if item.get("name") != car_mark:
                car_model_id = item.get("id")
                car_model = item.get("name")
                yield response.follow("https://vgparts.ge/api/product/bycriteria/0/" + str(car_model_id), callback = self.parse_part_list,
                                      meta = {"car_mark": car_mark, "car_model": car_model})
                
    def parse_part_list(self, response):
        json_data = json.loads(response.text)
        car_mark = response.meta["car_mark"]
        car_model= response.meta["car_model"]
        
        
        
        for data in json_data["result"]:
            item = NawilebiItem()
            item["website"] = "https://vgparts.ge/"
            item["part_url"] = "https://vgparts.ge/#/product/" + str(data.get('id'))
            item["car_mark"] = car_mark
            item["part_full_name"] = data.get("title")
            item["car_model"] = car_model
            item["year"] = None
            item["price"] = data['price'].get('price') if data.get('price') else None
            item["in_stock"] = True
            item["start_year"] = None
            item["end_year"] = None
                
            yield item
    
    '''
    ### Can't process angular
    def parse(self, response):
        
        start_url = response.url
        
        car_marks = response.css("div.engoc-spv1 div.container div.row > div")
        
        for car_mark in car_marks:
            relative_url = car_mark.css("a::attr(href)").get()
            car_mark_2 = car_mark.css("a::attr(alt)").get()
            car_mark_url = "https://eap.ge" + relative_url
            
            yield response.follow(car_mark_url, callback = self.parse_car_mark,
                                  meta = {"start_url": start_url, "car_mark": car_mark_2})
            
    def parse_car_mark(self, response):
        start_url = response.meta["start_url"]
        car_mark = response.meta["car_mark"]
        
        product_list = response.css("div.tab-panel div.engoc-row-equal > div")
        
        for product in product_list:
            car_relative_url = product.css("a::attr(href)").get()
            car_model_year = product.css("a::attr(a)").get()
            car_url_full = "https://eap.ge" + car_relative_url
            yield response.follow(car_url_full, callback = self.parse_car_part_list,
                                  meta = {"start_url": start_url, "car_mark": car_mark, "car_model_year": car_model_year}) 

    def parse_car_part_list(self, response):
        start_url = response.meta["start_url"]
        car_mark = response.meta["car_mark"]
        car_model_year = response.meta["car_model_year"]
        
        car_part_list_url = str(response.url)
        
        last_digits= get_digits_after_last_slash(car_part_list_url)
        json_file_url = "https://vgparts.ge/api/product/bycriteria/0/" + str(last_digits)
        
        yield response.follow(json_file_url, callback = self.parse_json,
                              meta = {"start_url": start_url, "car_mark": car_mark, "car_model_year": car_model_year})
        
    def parse_json(self, response):
        start_url = response.meta["start_url"]
        car_mark = response.meta["car_mark"]
        car_model_year = response.meta["car_model_year"]
        
        #item = NawilebiItem()
        
        json_data = json.loads(response.text)
        
        for item in json_data["result"]:
            item = NawilebiItem()
            item["website"] = start_url
            item["part_url"] = "https://vgparts.ge/#/product/" + str(item.get('id'))
            item["car_mark"] = car_mark
            item["part_full_name"] = car_model_year
            item["year"] = None
            item["price"] = item['price'].get('price') if item.get('price') else None
            item["in_stock"] = True 
            
            yield item'''
            
            
        
        