import scrapy
from nawilebi.items import NawilebiItem

class VsautoSpider(scrapy.Spider):
    name = "vsauto"
    allowed_domains = ["vsauto.ge", "proxy.scrapeops.io"]
    start_urls = ["https://vsauto.ge/"]
    custom_settings = {
        'ITEM_PIPELINES': {
            "nawilebi.pipelines.NawilebiPipeline": 300,
            "nawilebi.pipelines.VsautoPipeline": 200,
            #"nawilebi.pipelines.YearProcessPipeline": 300,
            "nawilebi.pipelines.SaveToMySQLPipeline": 900
        },
        #'DOWNLOAD_DELAY': 0.5,
        'SCRAPEOPS_PROXY_ENABLED': True,
        "DOWNLOADER_MIDDLEWARES":{
            #'scrapeops_scrapy.middleware.retry.RetryMiddleware': 550,
            #'scrapy.downloadermiddlewares.retry.RetryMiddleware': None,
            "nawilebi.middlewares.FakeBrowserHeaderAgentMiddleware": 101,
            "scrapeops_scrapy_proxy_sdk.scrapeops_scrapy_proxy_sdk.ScrapeOpsScrapyProxySdk": 100
        }
    }
    

    def parse(self, response):
        car_marks_list_1 = response.css("#post-515 > div > div:nth-child(4) > div")
        car_marks_list_2 =response.css("#post-515 > div > div:nth-child(6) > div")
        
        
        for car_mark in car_marks_list_1:
            car_mark_url = car_mark.css("div div div figure a::attr(href)").get()
            
            yield response.follow(car_mark_url, callback = self.parse_car_mark)
            
        for car_mark in car_marks_list_2:
            car_mark_url = car_mark.css("div div div figure a::attr(href)").get()
            
            yield response.follow(car_mark_url, callback = self.parse_car_mark)
            
    def parse_car_mark(self, response):
        car_mark_name = response.css("body > div.website-wrapper > div > div.page-title.page-title-default.title-size-default.title-design-centered.color-scheme-dark > div > header > h1::text").get()
        car_models_list = response.css("article > div.entry-content > div > div > div > div > div > div > div")
        
        
        for car_model in car_models_list:
            car_model_url = car_model.css("div a::attr(href)").get()
            
            yield response.follow(car_model_url, callback = self.parse_part_list,
                                  meta = {"car_mark": car_mark_name})
            
    def parse_part_list(self, response):
        item = NawilebiItem()
        car_parts_list = response.css("body > div.website-wrapper > div > div.container > div > div > div.products.elements-grid.align-items-start.woodmart-products-holder.woodmart-spacing-30.pagination-pagination.row.grid-columns-3 > div")
        
        for car_part in car_parts_list:
            item["website"] = "https://vsauto.ge/"
            item["car_mark"] = response.meta["car_mark"]
            item["car_model"] = response.css("body > div.website-wrapper > div > div.page-title.page-title-default.title-size-default.title-design-centered.color-scheme-dark.with-back-btn.title-shop > div > div > div.shop-title-wrapper > h1::text").get()
            item["part_url"] = car_part.css("div div.product-element-top a::attr(href)").get()
            item["part_full_name"] = car_part.css("div .product-information h3 a::text").get()
            pre_price = car_part.css("div .product-information .product-rating-price .wrapp-product-price .price")
            item["year"] = None
            item["price"] = pre_price.css("ins span bdi::text").get() or pre_price.css("span bdi::text").get()
            item["original_price"] = pre_price.css("del span bdi::text").get()
            
            yield item

                
    
        
        
                
            
        
