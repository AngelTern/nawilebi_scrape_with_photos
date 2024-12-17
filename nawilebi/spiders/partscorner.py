import scrapy
from nawilebi.items import NawilebiItem

class PartscornerSpider(scrapy.Spider):
    name = "partscorner"
    allowed_domains = ["partscorner.ge"]
    start_urls = ["https://partscorner.ge/"]
    custom_settings = {
        'ITEM_PIPELINES': {
            "nawilebi.pipelines.NawilebiPipeline": 300,
            "nawilebi.pipelines.PartscornerPipeline": 200,
            #"nawilebi.pipelines.YearProcessPipeline": 300,
            "nawilebi.pipelines.SaveToMySQLPipeline": 900
        },
        #'DOWNLOAD_DELAY': 0.5,
    }
        
    def parse(self, response):
        car_mark_list = response.css("body > section > div > div > div > div:nth-child(3) > div > div > div > div > div > section:nth-child(3) > div > div > div, body > section > div > div > div > div:nth-child(3) > div > div > div > div > div > section:nth-child(4) > div > div > div,body > section > div > div > div > div:nth-child(3) > div > div > div > div > div > section:nth-child(5) > div > div > div")
        
        for car_mark in car_mark_list:
            relative_url = car_mark.css("div > div > div > div > div > div.shop-img > a::attr(href)").get()
            #car_mark_name = car_mark.css("div > div > div > div > div > div.shop-img > a img::attr(alt)").get()
            
            yield response.follow("https://partscorner.ge/" + relative_url, callback = self.part_mark_page,
                                  )

    def part_mark_page(self, response):
        sections = response.css("body > section > div > div > div > div:nth-child(2) > div > div > div > div > div > section")
        for section in sections:
            model_container = section.css("div.elementor-container div.elementor-row > div")
            for car_model in model_container:
                relative_url = car_model.css("div.shop-item div.shop-content a::attr(href)").get()
                
                if relative_url:
                    yield response.follow("https://partscorner.ge/" + relative_url, callback=self.parse_part_list)
        
    def parse_part_list(self, response):
        car_parts_list = response.css("body > section > section > div > div > div.col-lg-9.order-xs-1 > div.row.columns-3 > div")
        
        for car_part in car_parts_list:
            relative_url = car_part.css("div div.shop-img a::attr(href)").get()
            
            if relative_url:
                yield response.follow("https://partscorner.ge/" + relative_url, callback=self.part_part_page)

            
    def part_part_page(self,response):
        item = NawilebiItem()
        
        item["website"] = "https://partscorner.ge/"
        item["part_url"] = response.url        
        item["part_full_name"] = response.css("h1.product_title::text").get()
        item["car_mark"] = response.css("section.shop-details-section.light-bg.pt-80.pb-80 > div > div > div:nth-child(2) > div > table > tbody > tr:nth-child(1) > td > span > ul > li::text").get()
        item["car_model"] = response.css("section.shop-details-section.light-bg.pt-80.pb-80 > div > div > div:nth-child(2) > div > table > tbody > tr:nth-child(2) > td > span > ul > li::text").get()
        item["year"] = response.css("section.shop-details-section.light-bg.pt-80.pb-80 > div > div > div:nth-child(2) > div > table > tbody > tr:nth-child(3) > td > span > ul > li::text").get()
        item["start_year"] = None
        item["end_year"] = None
        item["price"] = response.css("section.shop-details-section.light-bg.pt-80.pb-80 > div > div > div:nth-child(2) > div > p > span > bdi::text").get()
        item["in_stock"] = response.css("section.shop-details-section.light-bg.pt-80.pb-80 > div > div > div:nth-child(2) > div > div.product_meta > span.sku_wrapper > span.sku::text").get()
        
        return item