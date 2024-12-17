import scrapy
from nawilebi.items import NawilebiItem
#from nawilebi.utilities.additional_functions import get_digits_after_last_slash, get_digits_after_last_equal
import json
import re


class TopautopartsSpider(scrapy.Spider):
    name = "topautoparts"
    allowed_domains = ["topautoparts.ge"]
    start_urls = ["https://topautoparts.ge/"]
    
    custom_settings = {
        'ITEM_PIPELINES': {
            "nawilebi.pipelines.NawilebiPipeline": 300,
            "nawilebi.pipelines.TopautopartsPipeline": 200,
            #"nawilebi.pipelines.YearProcessPipeline": 300,
            "nawilebi.pipelines.SaveToMySQLPipeline": 900
        },
        #'DOWNLOAD_DELAY': 0.5,
    }
    
    def get_digits_after_last_slash(self, string):
        match = re.search(r"/(\d+)(?=[^/]*$)", string)
        if match:
            return match.group(1)
        return None

    def get_digits_after_last_equal(self, string):
        match = re.search(r"=(\d+)(?=[^=]*$)", string)
        if match:
            return match.group(1)
        return None

    
    def parse(self, response):
        car_marks = response.css("section.categories__section div.container div.row > div")
        for car_mark in car_marks:
            car_mark_url = car_mark.css("div a::attr(href)").get()
            car_mark_name = car_mark.css("div a h2::text").get()
            car_mark_id = self.get_digits_after_last_slash(car_mark_url)
            if car_mark_url:
                yield response.follow(car_mark_url, callback=self.parse_car_mark,
                                      meta = {"car_mark_id": car_mark_id, "car_mark": car_mark_name})

    def parse_car_mark(self, response):
        car_models = response.css("div.shop__section div.container div.row div:nth-of-type(2) div div ul li")
        car_mark_id = response.meta["car_mark_id"]
        for car_model in car_models:
            car_model_url = car_model.css("a::attr(href)").get()
            car_model_id = self.get_digits_after_last_equal(car_model_url)
            car_model_name = car_model.css("a div:nth-of-type(2) h2::text").get()
            if car_model_url and car_model_name:
                yield response.follow(f"https://topautoparts.ge/products_ajax?category_id={car_mark_id}&sub_category={car_model_id}&sort_by=&price_min=&price_max=", callback=self.parse_car_model,
                                      meta={"car_model": car_model_name, "car_mark_id": car_mark_id, "car_model_id": car_model_id, "car_mark": response.meta["car_mark"],
                                            "next_page_number": 2})

    def parse_car_model(self, response):
        json_data = json.loads(response.text)
        car_model = response.meta["car_model"]
        car_mark = response.meta["car_mark"]
        
        products = json_data['products']['data']
        if products:
            for product in products:
                if product:
                    item = NawilebiItem()
                    id = product.get("id")
                    
                    item["website"] = "https://topautoparts.ge/"
                    item["part_url"] = "https://topautoparts.ge/product_detail/" + str(id)
                    item["part_full_name"] = product.get("title")
                    item["price"] = product.get("price")
                    item["car_mark"] = car_mark
                    item["car_model"] = car_model
                    
                    yield item

            next_page_number = response.meta["next_page_number"]
            car_mark_id = response.meta["car_mark_id"]
            car_model_id = response.meta["car_model_id"]
            next_page_url = f"https://topautoparts.ge/products_ajax?page={next_page_number}&category_id={car_mark_id}&sub_category={car_model_id}&sort_by=&price_min=&price_max="
            yield response.follow(next_page_url , callback = self.parse_car_model,
                                  meta = {"car_model": car_model, "car_mark": car_mark, "car_model_id": car_model_id,
                                          "car_mark_id": car_mark_id, "next_page_number": next_page_number +1})