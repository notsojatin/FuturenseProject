#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import yfinance as yf
import argparse
import atexit
import datetime
import logging
import schedule
import time
import json
import sys
from kafka import KafkaProducer
from kafka.errors import KafkaError, KafkaTimeoutError


# In[ ]:


logger_format = '%(asctime)-15s %(message)s'
logging.basicConfig(format=logger_format)
logger = logging.getLogger('test')
logger.setLevel(logging.DEBUG)


# In[ ]:


topic_name = 'stockTopic'
kafka_broker = '127.0.0.1:9092'


# In[ ]:


def fetch_symbol_price(symbol,producer):
  '''
  function to fetch price of the stock and push it to the producer instance
  of kafka
  :param symbol: symbol of the stock
  :param producer: instance of the kafka producer
  :return: None
  '''

  logger.info(f'Fetching stock price of {symbol}')
  try:
    try:
        price=yf.Ticker(symbol).info['currentPrice']
    except KeyError as e:
        try:
            price=yf.Ticker(symbol).info['regularMarketPrice']
        except Exception as e:
            logger.error("Stock Symbol error, please validate stock symbol, closing script")
            sys.exit(0)
    if price is None:
        logger.warning("Stock Symbol Price warning, price not received")
        return
    timestamp=datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%dT%H:%M:%SZ')
    payload={
        'StockSymbol':symbol,
        'Price':price,
        'Time':timestamp
    }
    producer.send(topic=topic_name, value=payload)
    logger.info(f'Received stock price of {symbol} at {timestamp} : {price}')
  except KafkaError as ke:
    logger.warning(f'Kafka Error {ke}')
  except Exception as e:
    logger.warning(f'Failed to fetch stock price of {symbol} caused by {e}')


# In[ ]:


def on_shutdown(producer):
  '''
  shutdown hook to be called before the shutdown
  :param producer: instance of a kafka producer
  :return: None
  '''
  try:
    logger.info('Flushing pending messages to kafka, timeout is set to 10s')
    producer.flush(10) 
    logger.info('Finish flushing pending messages to kafka')
  finally:
      try:
        logger.info('Closing the Kafka connection')
        producer.close(10)
      except Exception as e:
        log_exception('Failed to close kafka connection',e)


# In[ ]:


if __name__=='__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument('symbol', help='provide Stock Symbol')
    args = parser.parse_args()
    symbol=args.symbol
#     symbol='gc=f'
    
    producer=KafkaProducer(
        bootstrap_servers=kafka_broker,
        value_serializer=lambda x: json.dumps(x).encode('utf-8')
    )
    schedule.every(1).second.do(fetch_symbol_price,symbol,producer)
    atexit.register(on_shutdown,producer)
    while True:
        schedule.run_pending()

