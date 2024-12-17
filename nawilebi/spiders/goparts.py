import scrapy
from nawilebi.items import NawilebiItem

class GopartsSpider(scrapy.Spider):
    name = "goparts"
    allowed_domains = ["goparts.ge"]
    start_urls = ["https://goparts.ge/ge"]
    custom_settings = {
        'ITEM_PIPELINES': {
            "nawilebi.pipelines.NawilebiPipeline": 300,
            "nawilebi.pipelines.GopartsPipeline": 200,
            #"nawilebi.pipelines.YearProcessPipeline": 300,
            "nawilebi.pipelines.SaveToMySQLPipeline": 900
        },
        #'DOWNLOAD_DELAY': 0.5,
    }

    def parse(self, response):
        car_mark_list = response.css("body > div.banner.bgwhite.p-t-40.p-b-40 > div > div > div")

        for car_mark in car_mark_list:
            relative_url = car_mark.css("div div a::attr(href)").get()
            car_mark_name = car_mark.css("div div a::text").get()

            yield response.follow(relative_url, callback=self.parse_car_mark_page,
                                  meta={"car_mark": car_mark_name})

    def parse_car_mark_page(self, response):
        car_models_list = response.css("#items > div")

        for car_model in car_models_list:
            relative_url = car_model.css("div div.block2-txt a::attr(href)").get()
            car_model_name = car_model.css("div div.block2-txt a::text").get()

            yield response.follow(relative_url, callback=self.parse_car_model_page,
                                  meta={"car_model": car_model_name, "car_mark": response.meta["car_mark"]})

    def parse_car_model_page(self, response):
        car_part_list = response.css("#items > div")

        for car_part in car_part_list:
            item = NawilebiItem()
            item["website"] = "https://goparts.ge/ge"
            item["part_url"] = car_part.css("div div.block2-txt a::attr(href)").get()
            item["car_mark"] = response.meta["car_mark"]
            item["car_model"] = response.meta['car_model']
            item["part_full_name"] = car_part.css("div div.block2-txt a::text").get()
            item["price"] = car_part.css("div div.block2-txt > span::text").get().strip()
            '''if price_raw:
                price = price_raw.replace("₾", "").strip()
            else:
                price = None
                '''
            yield item
    
    '''def parse_car_model_page(self, response):
        car_part_list = response.css("#items > div")

        for car_part in car_part_list:
            website = "https://goparts.ge/ge"
            part_url = car_part.css("div div.block2-txt a::attr(href)").get()
            car_mark = response.meta["car_mark"]
            car_model = response.meta["car_model"]
            part_full_name = car_part.css("div div.block2-txt a::text").get()

            price_raw = car_part.css("div div.block2-txt .block2-price::text").get()
            if price_raw:
                price = price_raw.replace("₾", "").strip()
            else:
                price = None

            year = None
            start_year = None
            end_year = None

            in_stock_block = car_part.css("div div.block2-txt div.in_stock p")
            if in_stock_block:
                for stock in in_stock_block:
                    item = NawilebiItem()
                    item["website"] = website
                    item["part_url"] = part_url
                    item["car_mark"] = car_mark
                    item["car_model"] = car_model
                    item["part_full_name"] = part_full_name
                    item["price"] = price if price != '' else None
                    item["year"] = year
                    item["start_year"] = start_year
                    item["end_year"] = end_year

                    # Extract stock-specific information
                    stock_class = stock.css("span::attr(class)").get()
                    city = stock.css("span::text").get()

                    item["in_stock"] = stock_class
                    item["city"] = city

                    yield item
            else:
                item = NawilebiItem()
                item["website"] = website
                item["part_url"] = part_url
                item["car_mark"] = car_mark
                item["car_model"] = car_model
                item["part_full_name"] = part_full_name
                item["price"] = price if price != '' else None
                item["year"] = year
                item["start_year"] = start_year
                item["end_year"] = end_year

                item["in_stock"] = None
                item["city"] = None

                yield item'''


            
