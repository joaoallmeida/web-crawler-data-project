import scrapy
from urllib.parse import urljoin

class AmazonSpider(scrapy.Spider):
    name='amazon'
    start_urls = ['https://www.amazon.com.br/']

    def parse(self, response):
        best_sellears_page = response.xpath('//*[@id="nav-xshop"]/a[2]')
        for page in best_sellears_page:
            yield response.follow(page,self.parse_next_tab)
        
    def parse_next_tab(self,response):
        for tab in response.xpath('//*[@id="zg_header"]/div//ul//a'):
            yield response.follow(tab, self.parse_department)

    def parse_department(self, response):
        for link in response.xpath("//div[@role='group']/div/a"):
            product_page = link.css('a::attr(href)').get()
            if product_page is not None:
                yield response.follow(product_page, self.parse_product_details)
    
    def parse_product_details(self, response):
        
        h1 = response.css('h1::text').get()
        depatment = h1.split('em ')[-1]
        type = h1.split(' em')[0]

        for detail in response.css('div#gridItemRoot'):
            yield {
                "type": type,
                "department": depatment,
                "rank": detail.css('span.zg-bdg-text::text').get(),
                "product": detail.css('div::text').get(),
                "rating_stars": detail.css('span.a-icon-alt::text').get(),
                "ratings": detail.css('span.a-size-small::text').get(),
                "price": str(detail.css('span::text').getall()[-1]).replace('\xa0','')
            }

        next_page = response.css('.a-last a::attr(href)').get()
        if next_page is not None:
           yield response.follow(next_page, callback=self.parse_product_details)