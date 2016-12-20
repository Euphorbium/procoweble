# procoweble
A Simple Producer/Consumer Web Link Extractor

Requires redis and rabbitmq servers.

Set connection settings in settings.py

Once you have everything set up, run `python producer.py list.txt 4` 
First argument is a filepath to a file with a list of links, one per line. 
Second argument sets how many webpages should a producer try to get concurrently.
Producer stores the sources of the links in rabbitmq queue.

You can start consumer.py workers without any parameters `python consumer.py` . They will consume links form the queue, extract links from documents, and store the results in redis database set, so only unique links are stored. 
Only  http links are stored.

Consumers also print unique results to stdout, and work even without redis.