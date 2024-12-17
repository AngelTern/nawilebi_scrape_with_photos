import scrapy
from nawilebi.items import NawilebiItem

class BgautoSpider(scrapy.Spider):
    name = "bgauto"
    allowed_domains = ["bgauto.ge"]
    start_urls = ["https://bgauto.ge/"]
    custom_settings = {
        'ITEM_PIPELINES': {
            "nawilebi.pipelines.NawilebiPipeline": 300,
            "nawilebi.pipelines.BgautoPipeline": 200,
            #"nawilebi.pipelines.YearProcessPipeline": 300,
            "nawilebi.pipelines.SaveToMySQLPipeline": 900
        },
        #'DOWNLOAD_DELAY': 0.5,
    }
    
    
    def parse(self, response):
        car_mark_list = response.css("body > main > section.product_area.mb-50.mt-3 > div > div.row > div > div > div")
        
        for car_mark in car_mark_list:
            model_page_url = car_mark.css("div a::attr(href)").get()
            car_mark_name = car_mark.css("div a h4::text").get().upper()
            
            yield response.follow(model_page_url, callback = self.parse_model_page,
                                  meta = {"car_mark": car_mark_name})
            
    def parse_model_page(self, response):
        car_model_list = response.css("body > main > div > div > div > div.col-xl-9.col-lg-8.shop-col-width-lg-8 > div > div > ul > li")
        
        for car_model in car_model_list:
            part_list_url = car_model.css("a::attr(href)").get()
            car_model_name = car_model.css("a div.categories__content h2::text").get().upper()
            
            yield response.follow(part_list_url, callback = self.parse_part_list,
                                  meta = {"car_model": car_model_name, "car_mark": response.meta["car_mark"]})
            
    def parse_part_list(self, response):
        part_list =response.css("#product_grid > div > div > div")
        
        for part in part_list:
            item = NawilebiItem()
            item["website"] = "https://bgauto.ge/"
            item["car_model"] = response.meta["car_model"]
            item["car_mark"] = response.meta["car_mark"]
            item["year"] = None
            item["start_year"] = None
            item["end_year"] = None
            item["part_url"] = part.css("article div:nth-of-type(2) h3 a::attr(href)").get()
            item["part_full_name"] = part.css("article div:nth-of-type(2) h3 a::text").get()
            in_stock = part.css("article div:nth-of-type(2) ul li span::text").get()
            item["in_stock"] = False if in_stock == "არ არის მარაგში" else True
            item["price"] = part.css("article div:nth-of-type(2) div.product__card--price span::text").get()
            item["original_price"] = None
            
            yield item
        
        navigation_list = response.css("body > main > div > div > div > div.col-xl-9.col-lg-8.shop-col-width-lg-8 > div > div > div.pagination__area > nav > ul > li")
        navigation_list = navigation_list[1:-1]
        
        for navigation in navigation_list:
            if "active" not in navigation.css("::attr(class)").get():
                next_part_page_url = navigation.css("a::attr(href)").get()
                
                yield response.follow(next_part_page_url, callback = self.parse_part_next_list,
                                      meta = {"car_model": response.meta["car_model"], "car_mark": response.meta["car_mark"]})
                
    def parse_part_next_list(self, response):
        part_list =response.css("#product_grid > div > div > div")
        
        for part in part_list:
            item = NawilebiItem()
            item["website"] = "https://bgauto.ge/"
            item["car_model"] = response.meta["car_model"]
            item["car_mark"] = response.meta["car_mark"]
            item["year"] = None
            item["start_year"] = None
            item["end_year"] = None
            item["part_url"] = part.css("article div:nth-of-type(2) h3 a::attr(href)").get()
            item["part_full_name"] = part.css("article div:nth-of-type(2) h3 a::text").get()
            in_stock = part.css("article div:nth-of-type(2) ul li span::text").get()
            item["in_stock"] = False if in_stock == "არ არის მარაგში" else True
            item["price"] = part.css("article div:nth-of-type(2) div.product__card--price span::text").get()
            item["original_price"] = None
            
            yield item