# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class NawilebiItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    website = scrapy.Field()
    part_url = scrapy.Field()
    car_mark = scrapy.Field()
    part_full_name = scrapy.Field()
    alternative_name_1 = scrapy.Field()
    alternative_name_2 = scrapy.Field()
    alternative_name_3 = scrapy.Field()
    alternative_name_4 = scrapy.Field()
    alternative_name_5 = scrapy.Field()
    alternative_name_6 = scrapy.Field()
    car_model = scrapy.Field()
    year = scrapy.Field()
    start_year = scrapy.Field()
    end_year = scrapy.Field()
    price = scrapy.Field()
    original_price = scrapy.Field()
    in_stock = scrapy.Field()
    city = scrapy.Field()
    phone = scrapy.Field()
    image_urls = scrapy.Field()
    images = scrapy.Field()
    pass
