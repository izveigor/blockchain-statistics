# Blockchain statistics [![GitHub license](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/izveigor/blockchain-statistics/blob/main/LICENSE) ![Tests](https://github.com/izveigor/blockchain-statistics/actions/workflows/tests.yml/badge.svg)
Django-powered application about blockchain statistics (bitcoin).
Application takes information from https://www.blockchain.com/ in real time (with WebSocket),
After that data is analyzed and showed the user.

![1](https://user-images.githubusercontent.com/68601180/155368619-7088e32a-31a0-46cb-b930-cbf6add55faa.JPG)
![2](https://user-images.githubusercontent.com/68601180/155368750-776f3ea8-f2a2-421a-836e-daeb158f107b.JPG)

## Installation
If you want to download some latest blocks, change src/entrypoint.sh file:
```
#!bin/sh
if [ ! -f db.sqlite3 ]; then
    python3 manage.py migrate
    # You can download blocks from 0 to 10
    python3 manage.py download_blocks [0 to 10]
fi
exec "$@"
```
To start application, you can use docker-compose up:
```
$ docker-compose -f docker-compose.prod.yml up --build
```
After that, meet 'localhost:1337'

## Application's components:
Main page of application includes three components (windows),
which show the user to data about blockchain.

## Live blockchain update
The component shows all recently blocks, that were added by the database.
The component will periodically updates, because the application works in real time.

### Block fields
* Height
* Index
* Hash
* Time (Unix time)

## Bitcoin statistics
The component shows statistics, take from all blocks in the database.
The component will periodically update, because the application works in real time.

### Bitcoin statistics fields
About blockchain:
* Number of satoshi
* Number of blocks
* Number of transactions
* Last update (Unix time)
---
Last block:
* Last block
* The largest transaction for inputs
* The largest transaction for outputs
* The most expensive transaction
---
About blocks:
* The most expensive block
* The cheapest block
* The largest number of transactions
* The least number of transactions
---
About transactions:
* The largest transaction for inputs
* The largest transaction for outputs
* The most expensive transaction

### About price
Price of transaction was calculated by all bitcoins, that were sent by inputs to other users
(except of outputs, when user sent bitcoins to yourself).

## Blockchain timeline
The component has next functions:
1) Enumeration all fields of blockchain with data of this period.
2) Compare status of blockchains (Bitcoin statistics)
---
To get the above data, necessary fill next data:
* Start date
* Start time
* End date
* End time

### About time
Application uses UTC time standard (UT0).
