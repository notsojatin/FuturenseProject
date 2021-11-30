#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from kafka import KafkaConsumer
from kafka.errors import KafkaError, KafkaTimeoutError
import atexit
import logging
import json
from pymongo import MongoClient
import pprint
import argparse
from datetime import datetime


# In[ ]:


logger_format = '%(asctime)-15s %(message)s'
logging.basicConfig(format=logger_format)
logger = logging.getLogger('test')
logger.setLevel(logging.DEBUG)


# In[ ]:


topic_name = 'transformedStockTopic'
# topic_name = 'stockTopic'
kafka_broker = '127.0.0.1:9092'
mongo_client='localhost:27017'
db_name='stock_test_final'
collection_name='stock_price_test_final'
input_datetime_format="%Y-%m-%dT%H:%M:%S.%f%z"
output_datetime_format="%Y-%m-%dT%H:%M:%SZ"


# In[ ]:


def dump_data(stock_data,collection):
  '''
  function to store data in MongoDB from Kafka
  :param data: stock data json
  :param collection: mongo collection session
  :return: None
  '''

  try:
    logger.info(f'Dumping data in MongoDB {json.dumps(stock_data)}')
    collection.replace_one({'_id':stock_data['_id']},stock_data,upsert=True)
    logger.info(f'Data dumped in MongoDB {json.dumps(stock_data)}')
  except KafkaError as ke:
    logger.warning(f'Kafka Error {ke}')
  except Exception as e:
    logger.warning(f'Failed to dump data {stock_data} due to {e}')


# In[ ]:


def on_shutdown(consumer):
  '''
  shutdown hook to be called before the shutdown
  :param consumer: instance of a kafka consumer
  :return: None
  '''
  try:
    logger.info('Closing Kafka Consumer')
    consumer.close()
    logger.info('Kafka Consumer Close')
  except KafkaError as ke:
    logger.warning(f'Failed to close Kafka Consumer, due to {ke}')
  finally:
      logger.info("Consumer Session closed")


# In[ ]:


def createCollectionMongo():
    '''
    function to create mongo session which will be used to write data
    to mongo client
    :return: none
    '''
    client = MongoClient(mongo_client)
    db = client[db_name]
    collection = db[collection_name]
    collection.create_index('StockSymbol', name="stock_symbol_index")
    return collection


# In[ ]:


if __name__=='__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument('client', help='client id of the consumer')
    args = parser.parse_args()
    client_id_cli=args.client
    
    consumer=KafkaConsumer(
        topic_name,
        bootstrap_servers=kafka_broker,
        value_deserializer=lambda x: json.loads(x.decode('utf-8')),
        auto_offset_reset='latest',
        group_id='my-group',
        client_id=client_id_cli
    )
    
    collection_session=createCollectionMongo()
  
    atexit.register(on_shutdown,consumer)

    for msg in consumer:
        data=msg.value
        data['_id']=f"{data['StockSymbol']}_{data['end']}"
        data['start_md']=datetime.strftime(datetime.strptime(data['start'],input_datetime_format),output_datetime_format)
        data['end_md']=datetime.strftime(datetime.strptime(data['end'],input_datetime_format),output_datetime_format)
        dump_data(data,collection_session)


# In[ ]:




