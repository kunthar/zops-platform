# -*-  coding: utf-8 -*-

import pika

connection = pika.BlockingConnection(pika.ConnectionParameters(
    host='35.198.115.35',
    port=5672,
    virtual_host='zopsm',
    credentials=pika.PlainCredentials('zopsm', 'chauj5DuXu7Eirirzohl1Eo3dewooNg6')
))

channel = connection.channel()

channel.basic_publish(
    exchange='messages',
    routing_key='testUser1',
    body='zeta grup mesajı'
)

channel.basic_publish(
    exchange='',
    routing_key='testUser5',
    body='example direct message'
)
