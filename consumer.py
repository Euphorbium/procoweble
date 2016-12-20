import pika
import logging
import json
import redis
from lxml import html
from urllib.parse import urlsplit

import settings

connection = pika.BlockingConnection(pika.ConnectionParameters(
    host=settings.HOST, port=settings.PORT, virtual_host=settings.VIRTUAL_HOST,
    credentials=pika.PlainCredentials(settings.USER, settings.PASSWORD), **settings.OTHER_SETTINGS))
channel = connection.channel()
channel.queue_declare(settings.QUEUE_NAME, arguments={'x-max-length': settings.MAX_QUEUE_LENGTH})

redis_connection = redis.Redis(**settings.REDIS)

def consumer(ch, method, properties, body):
    message = json.loads(body.decode())
    logging.info('Parsing: '+ message['link'])
    try:
        url = urlsplit(message['link'])
        base_url = '{scheme}://{netloc}/'.format(scheme=url.scheme, netloc=url.netloc)
        source = html.fromstring(message['source'])
        source.make_links_absolute(base_url=base_url)
        links = source.xpath('//a/@href')
        links = set(filter(lambda l: l.startswith('http'), links))
        print(message['link']+', '+" ".join(links))
        try:
            redis_connection.sadd(message['link'], *links)
        except:
            logging.error('Failed to write results to redis '+ message['link'])
    except Exception as e:
        logging.error(e, exc_info=True)


if __name__ == '__main__':
    channel.basic_consume(consumer,
                          queue=settings.QUEUE_NAME,
                          no_ack=True)

    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()
