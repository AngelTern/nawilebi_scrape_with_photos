import scrapy
from nawilebi.items import NawilebiItem

class PpSpider(scrapy.Spider):
    name = "pp"
    allowed_domains = ["pp.ge"]
    start_urls = ["https://pp.ge/"]
    custom_settings = {
        'ITEM_PIPELINES': {
            "nawilebi.pipelines.NawilebiPipeline": 300,
            "nawilebi.pipelines.PpPipeline": 200,
            #"nawilebi.pipelines.YearProcessPipeline": 300,
            "nawilebi.pipelines.SaveToMySQLPipeline": 900
        },
        #'DOWNLOAD_DELAY': 0.5,
    }
    
    
    def parse(self, response):
        car_mark_list= response.css("body > section.market-and-fullSearch > div.car_brands > div > div a")
        
        for car_mark in car_mark_list:
            car_mark_url = car_mark.css("::attr(href)").get()
            #car_mark_name = car_mark.css("div h2::text").get()
            
            yield response.follow(car_mark_url, callback = self.parse_mark_page,
                                  )
            
    def parse_mark_page(self, response):
        part_list = response.css("#car-par > div > div > div > div.card-wrapper-view > div")
        if part_list:
            for part in part_list:
                #car_mark = response.meta["car_mark"]
                part_url = part.css("div a::attr(href)").get()
                
                yield response.follow(part_url, callback = self.parse_part_page,
                                    )
            
        nav_list = response.css("ul.pagination li")
        if nav_list:
            for nav in nav_list:
                classes = nav.css("::attr(class)").get(default="")
                if "active" not in classes and "disabled" not in classes:
                    rel = nav.css("a::attr(rel)").get()
                    if rel is None:
                        href = nav.css("a::attr(href)").get()
                        if href:
                            yield response.follow(href, callback=self.parse_next_page)

    def parse_next_page(self, response):
        part_list = response.css("#car-par > div > div > div > div.card-wrapper-view > div")
        if part_list:
            for part in part_list:
                item = NawilebiItem()
                #car_mark = response.meta["car_mark"]
                part_url = part.css("div a::attr(href)").get()
                
                yield response.follow(part_url, callback = self.parse_part_page
                                    )
                
    def parse_part_page(self, response):
        item = NawilebiItem()
        
        item["part_url"] = response.url
        item["website"] = "https://pp.ge/"
        item["part_full_name"] = response.css("#car-parts-wrapper-view > div > div.product_right > div.prod_price > a > h2 ::text").get()
        item["car_mark"] = response.css("#car-parts-wrapper-view > div > div.product_right > div.prod_main_info > div:nth-child(1) > span:nth-child(1) > p ::text").get()
        item["car_model"] = response.css("#car-parts-wrapper-view > div > div.product_right > div.prod_main_info > div.prod_main_info_list.secc > span:nth-child(1) ::text").getall()
        item["year"] = response.css("#car-parts-wrapper-view > div > div.product_right > div.prod_main_info > div:nth-child(5) > span:nth-child(1) ::text").getall()
        item["in_stock"] = response.css("#car-parts-wrapper-view > div > div.product_right > div.prod_details_tab > span > div.wrapper_product_amo > p ::text").get()
        item["start_year"] = None
        item["end_year"] = None
        
        item["price"] = response.css("#car-parts-wrapper-view > div > div.product_right > div.prod_price > div > div ::text").getall()
        original_price = response.css("#car-parts-wrapper-view > div > div.product_right > div.prod_price > div > h3 ::text").getall()
        if original_price:
            item["original_price"] = original_price
            
        yield item