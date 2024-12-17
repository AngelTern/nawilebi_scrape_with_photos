import scrapy
from nawilebi.items import NawilebiItem

class GeopartsSpider(scrapy.Spider):
    name = "geoparts"
    allowed_domains = ["geoparts.ge"]
    start_urls = ["https://geoparts.ge/product-category/lexus-ge/", "https://geoparts.ge/product-category/tesla-2/", "https://geoparts.ge/product-category/toyota-ge/",
                  "https://geoparts.ge/product-category/ford-ge/", "https://geoparts.ge/product-category/nissan-ge/", "https://geoparts.ge/product-category/volkswagen-ge/",
                  "https://geoparts.ge/product-category/jeep/", "https://geoparts.ge/product-category/kia-ge/", "https://geoparts.ge/product-category/chevrolet-ge/", 
                  "https://geoparts.ge/product-category/buick/"]
    
    custom_settings = {
        'ITEM_PIPELINES': {
            "nawilebi.pipelines.NawilebiPipeline": 300,
            "nawilebi.pipelines.GeopartsPipeline": 200,
            #"nawilebi.pipelines.YearProcessPipeline": 300,
            "nawilebi.pipelines.SaveToMySQLPipeline": 900
        },
        #'DOWNLOAD_DELAY': 0.5,
    }
    
    def __init__(self, *args, **kwargs):
        super(GeopartsSpider, self).__init__(*args, **kwargs)
        self.parsed_pages = set()

    '''def parse(self, response):
        car_mark_list = response.css(
            "#content > div > section.elementor-section.elementor-top-section.elementor-element.elementor-element-4de1319.elementor-section-boxed.elementor-section-height-default.elementor-section-height-default > div.elementor-container.elementor-column-gap-default > div, "
            "#content > div > section.elementor-section.elementor-top-section.elementor-element.elementor-element-1e44530f.elementor-section-boxed.elementor-section-height-default.elementor-section-height-default > div.elementor-container.elementor-column-gap-default > div"
        )

        for car_mark in car_mark_list:
            car_model_url = car_mark.css("div div div h2 a::attr(href)").get() or car_mark.css("div div div a::attr(href)").get()
            car_mark_name = car_mark.css("div div div h2 a::text").get()

            if car_mark_name == "სალიკვიდაციო საქონელი":
                continue

            if car_model_url:
                yield response.follow(car_model_url, callback=self.parse_model_page)'''

    '''def parse_model_page(self, response):'''
    def parse(self, response):
        car_model_list = response.css("#content > div > div > div > section.elementor-section > div > div > div > div > div > div > ul > li")
        
        for car_model in car_model_list:
            part_page_url = car_model.css("a::attr(href)").get()
            
            if part_page_url not in self.parsed_pages:
                self.parsed_pages.add(part_page_url)
                yield response.follow(part_page_url, callback=self.parse_part_page)



    def parse_part_page(self, response):
        item = NawilebiItem()
        
        car_mark = response.css("#content > div > div > div > section > div > div > div > div.elementor-element > div > nav > a:nth-child(3)::text").get().upper()
        car_model = response.css("#content > div > div > div > section > div > div > div > div.elementor-element > div > nav::text").get().upper()
        if car_mark and car_mark == "ᲢᲝᲘᲝᲢᲐ":
            car_mark = "TOYOTA"
        car_part_list = response.css("#content > div > div > div > section > div > div > div > div.elementor-element > div > div > ul > li")
        
        for car_part in car_part_list:
            item["part_url"] = car_part.css("a::attr(href)").get()
            item["part_full_name"] = car_part.css("a h2::text").get()
            item["website"] = "https://geoparts.ge/"
            item["car_mark"] = car_mark
            item["car_model"] = car_model
            item["year"] = None
            item["start_year"] = None
            item["end_year"] = None
            
            price_span = car_part.css("a span.price")
            
            if price_span.css("del"):
                item["original_price"] = price_span.css("del span bdi::text").get()
                item["price"] = price_span.css("ins span bdi::text").get()
            else:
                item["price"] = price_span.css("span bdi::text").get()
                
            yield item
        
        page_navigation_list = response.css("#content > div > div > div > section > div > div > div > div.elementor-element > div > div > nav > ul > li")
        
        for page_navigation in page_navigation_list:
            next_page_url = page_navigation.css("a::attr(href)").get()
            if next_page_url and "next" in page_navigation.css("a::attr(class)").get():
                if next_page_url not in self.parsed_pages:
                    self.parsed_pages.add(next_page_url)
                    yield response.follow(next_page_url, callback=self.parse_next_part_pages)
                    
    def parse_next_part_pages(self, response):
        item = NawilebiItem()
        
        car_mark = response.css("#content > div > div > div > section > div > div > div > div.elementor-element > div > nav > a:nth-child(3)::text").get().upper()
        car_model = response.css("#content > div > div > div > section > div > div > div > div.elementor-element > div > nav > a:nth-child(5)::text").get().upper()
        if car_mark and car_mark == "ᲢᲝᲘᲝᲢᲐ":
            car_mark = "TOYOTA"
            
        car_part_list = response.css("#content > div > div > div > section > div > div > div > div.elementor-element > div > div > ul > li")
        
        for car_part in car_part_list:
            item["part_url"] = car_part.css("a::attr(href)").get()
            item["part_full_name"] = car_part.css("a h2::text").get()
            item["website"] = "https://geoparts.ge/"
            item["car_mark"] = car_mark
            item["car_model"] = car_model
            item["year"] = None
            item["start_year"] = None
            item["end_year"] = None
            
            price_span = car_part.css("a span.price")
            
            if price_span.css("del"):
                item["original_price"] = price_span.css("del span bdi::text").get()
                item["price"] = price_span.css("ins span bdi::text").get()
            else:
                item["price"] = price_span.css("span bdi::text").get()
                
            yield item
        
        
