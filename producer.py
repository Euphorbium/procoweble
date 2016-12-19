import pika
import requests
import logging
import sys
import json
import multiprocessing

import settings

connection = pika.BlockingConnection(pika.ConnectionParameters(
    host=settings.HOST, port=settings.PORT, virtual_host=settings.VIRTUAL_HOST,
    credentials=pika.PlainCredentials(settings.USER, settings.PASSWORD), **settings.OTHER_SETTINGS))
channel = connection.channel()
channel.queue_declare(settings.QUEUE_NAME, arguments={'x-max-length': settings.MAX_QUEUE_LENGTH})

def get_page(url):
    logging.info('getting: '+url)
    try:
        r = requests.get(url, timeout=settings.TIMEOUT, headers={'User-Agent': settings.USER_AGENT})
    except Exception as e:
        logging.error('failed to get '+'url', exc_info=True)
        return None
    if r.status_code == 200:
        return r.text
    else:
        logging.warning(url+'response: '+str(r.status_code))
        return None

def produce(link):
    try:
        source = get_page(link)
        if source:
            channel.basic_publish(exchange='',
                              routing_key=settings.QUEUE_NAME,
                              body=json.dumps({'link': link, 'source': source}))
    except Exception as e:
        logging.error(e, exc_info=True)

if __name__=='__main__':
    links = open(sys.argv[1]).read().splitlines()
    workers = sys.argv[2]
    pool = multiprocessing.Pool(int(workers))
    pool.map(produce, links)
    connection.close()