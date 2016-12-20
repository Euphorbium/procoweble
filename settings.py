#Rabbitmq connection settings

HOST = 'localhost'
PORT = 5672
VIRTUAL_HOST = '/'
USER = 'guest'
PASSWORD = 'guest'
OTHER_SETTINGS = {} # a dict of other possible connection parameters, see https://pika.readthedocs.io/en/0.10.0/modules/parameters.html#connectionparameters

QUEUE_NAME = 'sources'
MAX_QUEUE_LENGTH = 1000 # None or 0 is unlimited
USER_AGENT = 'Procoweble/0.0.1'
TIMEOUT = 3 # how long to wait for the web server to respond, in seconds

REDIS = {} # redis server connection settings, defaults to localhost, port=6379 , db=0

try:
     from local_settings import *
except ImportError as e:
     pass