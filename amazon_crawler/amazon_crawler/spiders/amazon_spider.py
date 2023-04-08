import scrapy
from ..items import AmazonCrawlerItem
from urllib.parse import unquote

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
        for product_page in response.xpath("//div[@role='group']/div/a"):
            yield response.follow(product_page, self.parse_product_details)
    
    def parse_product_details(self, response):
        
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
            item['brand'] = None
            item['asin'] = None
            item['producer'] = None

            # inside_page = detail.css('a::attr(href)').get()
            # if inside_page is not None:
            #     yield response.follow(inside_page, callback=self.parse_brand, cb_kwargs=dict(item=item))

            yield item

        next_page = response.css('.a-last a::attr(href)').get()
        if next_page is not None:
           yield response.follow(next_page, callback=self.parse_product_details)
    
    def parse_brand(self, response, item):

        tech_spec = response.xpath('//*[@id="productDetails_techSpec_section_1"]')
        detail_bullets = response.xpath('//*[@id="productDetails_detailBullets_sections1"]')

        try:
            brand_item = tech_spec.xpath('//tr[th[contains(text(),"Marca")]]/td/text()').get()
            asin_item = tech_spec.xpath('//tr[th[contains(text(),"ASIN")]]/td/text()').get()
            producer_item = tech_spec.xpath('//tr[th[contains(text(),"Fabricante")]]/td/text()').get()

            item['brand'] = brand_item.strip()
            item['asin'] = asin_item.strip()
            item['producer'] = producer_item.strip()

            if not item['asin']:
                asin_item = detail_bullets.xpath('//tr[th[contains(text(),"ASIN")]]/td/text()').get()
                item['asin'] = asin_item.strip()

            if not item['brand']:
                brand_item = tech_spec.xpath('//tr[th[contains(text(),"Nome da marca")]]/td/text()').get()
                item['brand'] =brand_item.strip()
        except:
            pass
           
        yield item