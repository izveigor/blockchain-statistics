# Blockchain statistics [![GitHub license](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/izveigor/blockchain-statistics/LICENSE)
The django-powered application about blockchain.
API site: https://www.blockchain.com/
## Opportunities:
* Live update blocks
* Live update statistics about blockchain
* Search time period to see blockchain changes
## Installation
If you want to download some latest blocks, change the docker-compose file:
```
command: bash -c "python manage.py migrate && python manage.py download_blocks [number of blocks] && python manage.py runserver 0.0.0.0:8080 & python manage.py start_websocket"
```
The range of number of blocks from 1 to 10.

To start application, you can use docker-compose up
```
$ docker-compose up
```
After that, meet '127.0.0.1:8080'

## Blockchain fields
* Number of satoshi
* Number of blocks
* Number of transactions
* Last update
* Last block
* The most expensive block
* The cheapest block
* The largest number of transactions
* The least number of transactions
* The largest transactions for inputs
* The largest transactions for outputs
* The most expensive transactions

## Block fields
* Price
* Number of transactions
* Height
* Hash
* Time
* Block index

## Tests
If you want to start test on Windows, you should use wsl (see https://github.com/django/channels/issues/1207).
Also, don't forget about redis (change settings hosts and start docker redis)