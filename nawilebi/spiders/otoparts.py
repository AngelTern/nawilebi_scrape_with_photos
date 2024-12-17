import scrapy
from nawilebi.items import NawilebiItem

class OtopartsSpider(scrapy.Spider):
    name = "otoparts"
    allowed_domains = ["otoparts.ge"]
    start_urls = ["https://otoparts.ge/dzaris-natsilebi/"]

    custom_settings = {
    'ITEM_PIPELINES': {
        "nawilebi.pipelines.NawilebiPipeline": 300,
        "nawilebi.pipelines.OtopartsPipeline": 200,
        "nawilebi.pipelines.SaveToMySQLPipeline": 900
    },
    'DOWNLOAD_DELAY': 5,
    "ROBOTSTXT_OBEY": False
    }
    
    def parse(self, response):
        car_mark_urls_list = response.css("div.elementor-177 section > div div div div div a::attr(href)").getall()
        
        for car_mark_url in car_mark_urls_list:
            yield response.follow(car_mark_url, callback = self.parse_mark_page)
            
    
    def parse_mark_page(self, response):
        model_links = response.css("body > div.elementor > section.elementor-section.elementor-top-section.elementor-section-boxed.elementor-section-height-default.elementor-section-height-default > div > div > div > section.elementor-section.elementor-inner-section.elementor-element.elementor-section-boxed.elementor-section-height-default.elementor-section-height-default > div > div.elementor-column.elementor-inner-column.elementor-element > div > div > div > div > div > h1 a::attr(href), body > div.elementor > section.elementor-section.elementor-top-section.elementor-section-boxed.elementor-section-height-default.elementor-section-height-default > div > div > div > section.elementor-section.elementor-inner-section.elementor-element.elementor-section-boxed.elementor-section-height-default.elementor-section-height-default > div > div.elementor-column.elementor-inner-column.elementor-element > div > div > div > div > div > h3 a::attr(href)").getall()
        
        for model_link in model_links:
            yield response.follow(model_link, callback = self.parse_model_page)
            
    def parse_model_page(self, response):
        part_urls = response.css("ul li.product div .premium-woo-products-details-wrap a.premium-woo-product__link::attr(href)").getall()
        
        for part_url in part_urls:
            yield response.follow(part_url, callback = self.parse_part_page)
            
    def parse_part_page(self, response):
        item = NawilebiItem()
        
        item["car_mark"] = response.css("nav.woocommerce-breadcrumb a:nth-of-type(2)::text").get()
        item["car_model"] = response.css("nav.woocommerce-breadcrumb a:nth-of-type(3)::text").get()
        item["part_url"] = response.url
        item["part_full_name"] = response.css("h1.product_title::text").get()
        item["price"] = response.css("div.elementor-widget-container p.price span.woocommerce-Price-amount bdi::text").get()
        
        in_stock = response.css("div.elementor-add-to-cart p.stock::text").get()
        item["in_stock"] = True if in_stock == "მარაგში" else False
        
        item["website"] = "https://otoparts.ge/"
        item["year"] = None
        item["start_year"] = None
        item["end_year"] = None
        
        yield item