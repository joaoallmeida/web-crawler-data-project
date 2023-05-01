
from datetime import datetime
import pandas as pd, numpy as np, awswrangler as wr
import boto3

awsSession = boto3.Session(region_name='us-east-1')

dt_ref = datetime.now().strftime("%Y%m%d") 
df = wr.s3.read_json(f's3://webscraping.com.br/scraping/raw/amazon_products_{dt_ref}.json',boto3_session=awsSession)

workDf = df.copy()
# workDf = workDf.rename({'_id':'id'}, axis=1)
workDf['price'] = workDf['price'].replace(r'[^0-9,]', '', regex=True).replace('',np.NaN).str.replace(',','.')
workDf['ratings'] = workDf['ratings'].replace(r"[a-zA-Z]+", np.NaN, regex=True)
workDf['stars'] = workDf['stars'].fillna('N/D')
workDf['department'] = workDf['department'].str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8')
workDf['product'] = workDf['product'].str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8')
workDf['product'] = workDf['product'].str.title()


floatColumns = ['price','ratings']
dateColumns = ['extract_at']
replaceRows = {'Esport':'Esporte','Saud':'Saude','Loja Kindl':'Loja Kindle'}

for col in floatColumns:
    workDf[col] = workDf[col].astype(float)

for col in dateColumns:
    workDf[col] = pd.to_datetime(workDf[col])

for key in replaceRows.keys():
    workDf['department'] = workDf['department'].replace(key,replaceRows[key])


wr.s3.to_parquet(
    df,
    f's3://webscraping.com.br/scraping/refined/amazon_products_{dt_ref}.parquet',
    boto3_session=awsSession
)