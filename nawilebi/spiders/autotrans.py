import scrapy
from nawilebi.items import NawilebiItem
#from nawilebi.utilities.additional_functions import adjust_for_next_url_autotrans

class AutotransSpider(scrapy.Spider):
    name = "autotrans"
    allowed_domains = ["autotrans.ge"]
    start_urls = ["https://autotrans.ge/products/"]
    custom_settings = {
        'ITEM_PIPELINES': {
            "nawilebi.pipelines.NawilebiPipeline": 300,
            "nawilebi.pipelines.AutotransPipeline": 200,
            #"nawilebi.pipelines.YearProcessPipeline": 300,
            "nawilebi.pipelines.SaveToMySQLPipeline": 900
        },
        "ROBOTSTXT_OBEY": False,
        #'DOWNLOAD_DELAY': 0.5,
        #'AUTOTHROTTLE_ENABLED': True,
        #'AUTOTHROTTLE_START_DELAY': 3,  
        #'AUTOTHROTTLE_MAX_DELAY': 60,   
        #'AUTOTHROTTLE_TARGET_CONCURRENCY': 1.0,
    }
    
    avoid_urls = [
        "https://autotrans.ge/product/102/",
        "https://autotrans.ge/product/gray-shoes/",
        "https://autotrans.ge/product/audi/",
        "https://autotrans.ge/product/honda/"
    ]
    
    
    '''-----------------------------------------'''
    '''page_count = 1
    
    def parse(self, response):
        part_url_list = response.css(".sitemap_table tbody tr")[5:]

        for part_url in part_url_list:
            part_url_full = part_url.css("td a::attr(href)").get()
        
            yield response.follow(part_url_full, callback = self.parse_part_page)
            
        self.parse_from_html_file()
    
    def parse_from_html_file(self):
        try:
            with open("nawilebi/nawilebi/spiders/manual_html/autotrans_page_2.html", 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            selector = Selector(text=html_content)
            part_url_list = selector.css(".sitemap_table tbody tr")
            
            for part_url in part_url_list:
                part_url_full = part_url.css("td a::attr(href)").get()
                yield scrapy.Request(url=part_url_full, callback=self.parse_part_page)
        except FileNotFoundError:
            self.logger.error("HTML file for the second page not found.")
            raise CloseSpider()
            
    
    def parse_part_page(self, response):
        item = NawilebiItem()
        item["website"] = "https://autotrans.ge/"
        item["part_url"] = response.url
        item["car_mark"] = response.css("#main > div > article > div.hero-section.ct-constrained-width > header > nav > span.item-0 > a > span::text").get()
        item["car_model"] = response.css("#main > div > article > div.hero-section.ct-constrained-width > header > nav > span.item-1 > a > span::text").get()
        item["year"] = None
        item["part_full_name"] = response.css("div > div.product-entry-wrapper.ct-constrained-width > div.summary.entry-summary.entry-summary-items > h1::text").get()
        item["price"] = response.css("div > div.product-entry-wrapper.ct-constrained-width > div.summary.entry-summary.entry-summary-items > p > span > ins > span > bdi::text").get()
        item["original_price"] = response.css("div > div.product-entry-wrapper.ct-constrained-width > div.summary.entry-summary.entry-summary-items > p > span > del > span > bdi::text").get()
        item["in_stock"] = True
        
        yield item'''
        
    '''------------------------------------------------------'''
        
    def parse(self, response):
        car_mark_list = response.css("#main > div > section > ul > li")
        
        for car_mark in car_mark_list:
            car_mark_name = car_mark.css("h2 a::text").get()
            car_mark_url = car_mark.css("h2 a::attr(href)").get()
            
            yield response.follow(car_mark_url, callback = self.parse_car_mark_page,
                                  meta = {"car_mark": car_mark_name})
            
    def parse_car_mark_page(self, response):
        car_model_list =response.css("#main > div > section > ul li")
        
        for car_model in car_model_list:
            car_model_name = car_model.css("h2 a::text").get()
            car_model_url = car_model.css("h2 a::attr(href)").get()
            
            yield response.follow(car_model_url, callback = self.parse_part_page,
                                  meta = {"car_mark": response.meta["car_mark"], "car_model": car_model_name})
            
    def parse_part_page(self, response):
        
        
        
        car_part_list = response.css("#main > div > section > ul > li")
        
        for car_part in car_part_list:
            item = NawilebiItem()
            part_url = car_part.css("h2 a::attr(href)").get()
            
            if part_url in self.avoid_urls:
                self.logger.info(f"Skipping URL: {part_url}")
                continue  # Skip this URL and continue with the next one

            item["part_full_name"] = car_part.css("h2 a::text").get()
            item["car_mark"] = response.meta["car_mark"]
            item["car_model"] = response.meta["car_model"]
            item["year"] = None
            item["part_url"] = part_url
            item["website"] = "https://autotrans.ge/"
            price_span = car_part.css("span.price span")
            
            if price_span.css("del"):
                item["original_price"] = car_part.css("span.price span del span bdi::text").get()
                item["price"] = car_part.css("span.price span ins span bdi::text").get()
            else:
                item["price"] = car_part.css("span.price span bdi::text").get()
                
            item["start_year"] = None
            item["end_year"] = None
            
            yield item
        
        if response.css(".ct-pagination"):
            pages_list = response.css(".ct-pagination div a::text").getall()

            for i in pages_list:
                #car_mark_adjusted, car_model_adjusted = adjust_for_next_url_autotrans(response.meta["car_mark"], response.meta["car_model"])

                #next_page_url = f"https://autotrans.ge/product-category/{car_mark_adjusted}/{car_model_adjusted}/page/{i}/"
                next_page_url = response.url + f"page/{i}/"
                yield response.follow(next_page_url, callback=self.next_page_parse,
                                      meta={"car_mark": response.meta["car_mark"], "car_model": response.meta["car_model"]})

    def next_page_parse(self, response):
        item = NawilebiItem()
        car_part_list = response.css("#main > div > section > ul > li")
        
        for car_part in car_part_list:
            part_url = car_part.css("h2 a::attr(href)").get()

            if part_url in self.avoid_urls:
                self.logger.info(f"Skipping URL: {part_url}")
                continue  # Skip this URL and continue with the next one

            item["part_full_name"] = car_part.css("h2 a::text").get()
            item["car_mark"] = response.meta["car_mark"]
            item["car_model"] = response.meta["car_model"]
            item["year"] = None
            item["part_url"] = part_url
            item["website"] = "https://autotrans.ge/"
            price_span = car_part.css("span.price span")
            
            if price_span.css("del"):
                item["original_price"] = car_part.css("span.price span del span bdi::text").get()
                item["price"] = car_part.css("span.price span ins span bdi::text").get()
            else:
                item["price"] = car_part.css("span.price span bdi::text").get()
                
            item["start_year"] = None
            item["end_year"] = None
            yield item