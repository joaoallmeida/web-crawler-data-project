import scrapy
from ..items import AmazonCrawlerItem
from urllib.parse import unquote, urlencode
from datetime import datetime

class AmazonSpider(scrapy.Spider):
    name='amazon'
    start_urls = ['https://www.amazon.com.br/']

    def parse(self, response):
        best_sellears_page = response.xpath('//*[@id="nav-xshop"]/a[2]')
        for page in best_sellears_page:
            yield response.follow(page,self.parse_tabs)
        
    def parse_tabs(self,response):
        for tab in response.xpath('//*[@id="zg_header"]/div//ul//a'):
            yield response.follow(tab, self.parse_department)

    def parse_department(self, response):
        for product_page in response.xpath("//div[@role='group']/div/a"):
            yield response.follow(product_page, self.parse_details)
    
    def parse_details(self, response):
        
        h1 = response.css('h1::text').get()
        last_index = h1.rfind('em')
        types,department = [h1[:last_index].strip(), h1[last_index:].strip('em ')]

        for detail in response.xpath("//div[@id='gridItemRoot']"):
            item = AmazonCrawlerItem()

            item['asin'] = str(detail.css('a::attr(href)').get()).split('/')[3]
            item['type'] = types
            item['department'] = department
            item['rank'] = int(str(detail.css('span.zg-bdg-text::text').get()).replace('#',''))
            item['product'] = detail.css('div::text').get()
            item['stars'] = detail.css('span.a-icon-alt::text').get()
            item['ratings'] = detail.css('span.a-size-small::text').get()
            item['price'] = str(detail.css('span::text').getall()[-1]).replace('\xa0','')
            item['link'] = unquote(response.urljoin(detail.css('a::attr(href)').get()))
            item['img'] = detail.css('img::attr(src)').get()
            item['extract_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            yield item
            
            # page = detail.css('a::attr(href)').get()
            # if page is not None:
            #     yield scrapy.Request(response.urljoin(page), callback=self.parse_asin, cb_kwargs={"item": item})


        next_page = response.css('.a-last a::attr(href)').get()
        if next_page is not None:
           yield response.follow(next_page, callback=self.parse_details)
    
    # def parse_asin(self, response, item):
    #     item['asin'] = response.xpath('//*[@data-asin]/@data-asin').get()
    #     yield item