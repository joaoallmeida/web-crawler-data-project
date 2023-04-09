import scrapy
from scrapy.shell import inspect_response
from ..items import AmazonCrawlerItem
from urllib.parse import unquote
from datetime import datetime
class AmazonSpider(scrapy.Spider):
    name='amazon'
    start_urls = ['https://www.amazon.com.br/']

    HEADERS = {
        "accept": "*/*",
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36",
        "accept-language": "pt-BR,pt;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        "accept-encoding": "gzip, deflate, br"
    }

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

            inside_page = detail.css('a::attr(href)').get()
            if inside_page is not None:
                yield response.follow(inside_page
                                    , callback=self.parse_brand
                                    , dont_filter=True
                                    # , headers=self.HEADERS
                                    # , errback=self.parse_brand
                                    , cb_kwargs={"item": item})

            # yield item

        next_page = response.css('.a-last a::attr(href)').get()
        if next_page is not None:
           yield response.follow(next_page, callback=self.parse_details)
    
    def parse_brand(self, response, item):

        print(f'Entrando na url: {response.url}')

        try:
            tech_spec = response.xpath('//*[@id="productDetails_techSpec_section_1"]')
            detail_bullets = response.xpath('//*[@id="productDetails_detailBullets_sections1"]')
            detail_feature = response.xpath('//*[@id="detailBullets_feature_div"]')

            brand_item = tech_spec.xpath('//tr[th[contains(text(),"Marca")]]/td/text()').get()
            asin_item = tech_spec.xpath('//tr[th[contains(text(),"ASIN")]]/td/text()').get()
            producer_item = tech_spec.xpath('//tr[th[contains(text(),"Fabricante")]]/td/text()').get()


            item['brand'] = brand_item
            item['asin'] = asin_item
            item['producer'] = producer_item

            print('To aqui no parse_brand')

            if not item['brand']:
                print('To dentro do if brand')
                brand_item = tech_spec.xpath('//tr[th[contains(text(),"Nome da marca")]]/td/text()').get()
                item['brand'] = brand_item

            if not item['asin']:
                print('To dentro do if asin')
                asin_item = detail_bullets.xpath('//tr[th[contains(text(),"ASIN")]]/td/text()').get()
                item['asin'] = asin_item
                
                if not item['asin']:
                    print('To dentro do if asin 2')
                    asin_item = detail_feature.xpath('//span[contains(span[@class="a-text-bold"]/text(), "ASIN")]/span[2]').get()
                    item['asin'] = asin_item


            print(brand_item, asin_item, producer_item, end='\n')
            print('To sando do parse_brand')

            yield item

        except Exception as e:
            pass