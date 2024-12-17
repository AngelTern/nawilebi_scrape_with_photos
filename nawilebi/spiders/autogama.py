import scrapy
from nawilebi.items import NawilebiItem

class AutogamaSpider(scrapy.Spider):
    name = "autogama"
    allowed_domains = ["autogama.ge", "proxy.scrapeops.io"]
    start_urls = ["https://autogama.ge/"]
    custom_settings = {
        'ITEM_PIPELINES': {
            "nawilebi.pipelines.NawilebiPipeline": 300,
            "nawilebi.pipelines.AutogamaPipeline": 200,
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
        car_mark_list = response.css("body > div.wp-site-blocks > div.wp-block-group > div > figure.wp-block-gallery figure")
        
        for car_mark in car_mark_list:
            mark_page_url = car_mark.css("a::attr(href)").get()
            if mark_page_url == "https://autogama.ge/?cat=60":
                yield response.follow(mark_page_url, callback = self.parse_model_page)
            else:
                yield response.follow(mark_page_url, callback = self.parse_mark_page)
            
    def parse_mark_page(self, response):
        car_model_list = response.css("body > div.wp-site-blocks > div > div > figure > figure")
        
        for car_model in car_model_list:
            part_list_url = car_model.css("a::attr(href)").get()
            
            yield response.follow(part_list_url, callback =self.parse_model_page)
            
    def parse_model_page(self, response):
        part_list = response.css("body > div.wp-site-blocks > div > div > figure > figure")
        
        for part in part_list:
            figcaption = part.css("figcaption")
            if figcaption:
                item = NawilebiItem()
                item["part_url"] = response.url
                item["website"] = self.start_urls[0]
                
                strong_element = response.css("figure > blockquote > p > strong::text")
                
                if len(strong_element) != 0:
                    item["car_model"] = response.css("figure > blockquote > p > strong::text").get().upper()
                else:
                    item["car_model"] =response.css("div.wp-site-blocks > div > div > div > figure > blockquote > p::text").get().upper()
                
               
                
                item["part_full_name"] = part.css("figcaption ::text").get()
                
                
                item["year"] = None
                item["start_year"] = None
                item["end_year"] = None
                item["car_mark"] = None
                item["price"] = None
                
                yield item
