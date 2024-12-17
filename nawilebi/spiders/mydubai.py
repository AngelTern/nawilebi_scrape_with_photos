import scrapy
from bs4 import BeautifulSoup
from nawilebi.items import NawilebiItem

class MydubaiSpider(scrapy.Spider):
    name = "mydubai"
    allowed_domains = ["mydubai.ge"]
    start_urls = ["https://mydubai.ge/wp-sitemap-posts-product-1.xml"]
    custom_settings = {
        'ITEM_PIPELINES': {
            "nawilebi.pipelines.NawilebiPipeline": 100,
            "nawilebi.pipelines.MydubaiPipeline": 200,
            #"nawilebi.pipelines.YearProcessPipeline": 300,
            "nawilebi.pipelines.SaveToMySQLPipeline": 900
        },
        'DOWNLOAD_DELAY': 0.5,
    }
    
    def parse(self, response):
        soup = BeautifulSoup(response.text, 'xml')
        urls = soup.find_all('loc')
        for url_tag in urls:
            
            url = url_tag.text  
            
            yield response.follow(url, callback = self.parse_part_page)
            
    def parse_part_page(self, response):
        item = NawilebiItem()
        
        item["website"] = "https://mydubai.ge/"
        item["phone"] = "557 38 15 00"
        item["part_url"] = response.url
        item["part_full_name"] = response.css("div.fitment-product-summary div.fitment-product-summary-inner span::text").get()
        item["price"] = response.css("div.fitment-product-summary div.fitment-product-summary-inner div.fitment-summary-item.fitment-price div.price span bdi::text").get().strip() if response.css("div.fitment-product-summary div.fitment-product-summary-inner div.fitment-summary-item.fitment-price div.price span bdi::text").get() else None
        item["car_model"] = response.css("div.fitment-product-summary div.fitment-product-summary-inner div.fitment-summary-item.fitment-product-meta div span.meta-value a::text").get().strip().upper()
        item["car_mark"] = response.css("div.fitment-product-summary div.fitment-product-summary-inner div.fitment-summary-item.fitment-product-top-nav nav a:nth-of-type(3)::text").get().strip().upper()
        
        yield item