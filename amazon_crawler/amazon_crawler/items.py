# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.item import Item,Field

class AmazonCrawlerItem(Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    type = Field()
    department = Field()
    rank = Field()
    brand = Field()
    product = Field()
    stars = Field()
    ratings = Field()
    price = Field()
    link = Field()
    img = Field()
    asin = Field()
    producer = Field()


