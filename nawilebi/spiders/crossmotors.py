import scrapy
from nawilebi.items import NawilebiItem

class CrossmotorsSpider(scrapy.Spider):
    name = "crossmotors"
    allowed_domains = ["www.crossmotors.ge"]
    start_urls = ["https://www.crossmotors.ge/"]
    custom_settings = {
        'ITEM_PIPELINES': {
            "nawilebi.pipelines.NawilebiPipeline": 300,
            "nawilebi.pipelines.CrossmotorsPipeline": 200,
            #"nawilebi.pipelines.YearProcessPipeline": 300,
            "nawilebi.pipelines.SaveToMySQLPipeline": 900
        },
        #'DOWNLOAD_DELAY': 10,
    }

    def parse(self, response):
        car_mark_list = response.css("#comp-lnprkq5o > div:nth-child(2) > div > div")

        for car_mark in car_mark_list:
            car_model_list_url = car_mark.css("div:nth-of-type(2) div div:nth-of-type(1) a::attr(href)").get()
            car_mar_name = car_mark.css("div:nth-of-type(2) div div:nth-of-type(2) h1 span span::text").get()

            if car_mar_name:
                car_mar_name = car_mar_name.strip()

            if car_model_list_url:
                yield response.follow(
                    car_model_list_url,
                    callback=self.parse_mark_page,
                    meta={"car_mark": car_mar_name}
                )

    def parse_mark_page(self, response):
        car_model_list = response.css("section div:nth-of-type(2) > div > div.KaEeLN")

        for car_model in car_model_list:
            part_page_url = car_model.css("div:nth-of-type(2) div div:nth-of-type(1) a::attr(href)").get()
            car_model_name = car_model.css("div:nth-of-type(2) div div:nth-of-type(2) h1 span span::text").get()

            if car_model_name:
                car_model_name = car_model_name.strip()

            if part_page_url:
                yield response.follow(
                    part_page_url,
                    callback=self.parse_part_list,
                    meta={
                        "car_mark": response.meta["car_mark"],
                        "car_model": car_model_name,
                        "page_number": 2,
                        "scraped_page": []
                    }
                )

    def parse_part_list(self, response):
        part_list = response.css("div > div > div > div > section > div > ul li")

        for part in part_list:
            if part.css("::attr(data-hook)").get() == 'product-list-grid-item':
                item = NawilebiItem()

                item["car_mark"] = response.meta["car_mark"]
                item["car_model"] = response.meta["car_model"]
                item["website"] = "https://www.crossmotors.ge/"
                item["part_url"] = part.css("div div a::attr(href)").get()
                item["part_full_name"] = part.css("div div div div a div div div div:nth-of-type(1) p::text").get()
                item["price"] = part.css("div div div div a div div div div:nth-of-type(2) div div span:nth-of-type(2)::text").get()
                item["year"] = None
                item["start_year"] = None
                item["end_year"] = None

                yield item

        scraped = response.meta["scraped_page"]
        for nav in part_list:
            if nav.css("::attr(data-hook)").get() == 'product-list-pagination-link-seo-link':
                next_page_url = nav.css("a::attr(href)").get()
                if next_page_url not in scraped:
                    scraped.append(next_page_url)
                    yield response.follow(
                        next_page_url,
                        callback=self.parse_part_list,
                        meta={
                            "car_mark": response.meta["car_mark"],
                            "car_model": response.meta["car_model"],
                            "page_number": response.meta["page_number"] + 1,
                            "scraped_page": scraped
                        }
                    )

            
        '''load_more_button = response.css("div > div > div > div > section > div > button")
        if load_more_button and load_more_button.css("::attr(data-hook)").get() == "load-more-button":
            yield response.follow(
                response.url + f"?page={response.meta['page_number']}",
                callback = self.parse_part_list,
                meta={
                    "car_mark": response.meta["car_mark"],
                    "car_model": response.meta["car_model"],
                    "page_number": str(int(response.meta["page_number"]) + 1)
                }
            )
        else:'''
