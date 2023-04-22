# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from datetime import datetime
import pymongo ,json ,boto3

class JsonFilePipeline:
    def open_spider(self, spider):
        # self.data = list()
        self.file = open('raw_data.json','w',encoding='utf-8')
    
    def close_spider(self, spider):
        # line = json.dumps(self.data, ensure_ascii=False)
        # self.file.write(line)
        self.file.close()

    def process_item(self, item, spider):
        # self.data.append((ItemAdapter(item).asdict()))
        line = json.dumps(ItemAdapter(item).asdict(), ensure_ascii=False) + '\n'
        self.file.write(line)
        return item

class MongoPipeline:

    collection_name = 'amazon_ecommerce'

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE', 'items')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        self.db[self.collection_name].insert_one(ItemAdapter(item).asdict())
        return item

class S3Pipeline:
    
    def __init__(self, region_name, s3_bucket):
        self.s3_bucket = s3_bucket
        self.awsSession = boto3.Session(region_name=region_name)

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            region_name=crawler.settings.get('AWS_REGION'),
            s3_bucket=crawler.settings.get('S3_BUCKET')
        )

    def open_spider(self, spider):
        self.data = list()
        self.s3_client = self.awsSession.client('s3')

    def close_spider(self, spider):
        dt_ref = datetime.now().strftime("%Y%m%d")    
        item_bytes = str(json.dumps(self.data,ensure_ascii=False)).encode('utf-8')
        self.s3_client.put_object(Bucket=self.s3_bucket, Key=f'scraping/raw/amazon_products_{dt_ref}.json', Body=item_bytes)

    def process_item(self, item, spider):
        self.data.append((ItemAdapter(item).asdict()))
        return item