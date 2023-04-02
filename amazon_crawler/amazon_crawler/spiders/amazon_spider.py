import scrapy

class AmazonSpider(scrapy.Spider):
    name='amazon'
    start_urls = ['https://www.amazon.com.br/']

    def parse(self, response):
        best_sellears_page = response.xpath('//*[@id="nav-xshop"]/a[2]')
        for a in best_sellears_page:
            yield response.follow(a,self.parse_best_sellears)
        
    def parse_best_sellears(self, response):
        for data in response.css('.a-inline-block .a-link-normal'):
            # yield {
            #     "label":data.css('.a-link-normal::attr(aria-label)').get(),
            #     "link": (data.css('.a-inline-block .a-link-normal::attr(href)').getall())
            #     }
            
            product_details = data.css('.a-link-normal::attr(href)').get()
            if product_details is not None:
                yield response.follow(product_details,self.parse_product_details)
    
    def parse_product_details(self, response):

        print(response.css('h1::text').get())
        
        for detail in response.css('div#gridItemRoot'):
            data = {
                "rank": detail.css('span.zg-bdg-text::text').get(),
                "product": detail.css('div::text').get(),
                "rating_stars": detail.css('span.a-icon-alt::text').get(),
                "rating": detail.css('span.a-size-small::text').get(),
                "price": str(detail.css('span::text').getall()[-1]).replce('\xa0','')
            }
            print(data)