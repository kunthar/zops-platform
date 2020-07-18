Buckets
=======

Bucket Name    | Service | Backend | TTL         | 2i   |
---------------|---------|---------|-------------|------|
Message        | roc     | leveldb | 30d         | x    |
Channel        | roc     | leveldb |             |      |
Invite         | roc     | leveldb |             |      |
Subscriber     | roc     | leveldb |             |      |
Push Message   | push    | leveldb | 30d         | x    |
Segment        | push    | leveldb |             | x    |
Tag            | push    | leveldb |             | x    |
Delivery Info  | push    | leveldb | 30d         |      |
Client         | push    | leveldb |             |      |
Target         | push    | leveldb |             |      |
Log            | admin   | leveldb | 7d          | x    |

Bucket Types
============

zopsm_rabbit_hook for Message bucket

zopsm_30d_ttl_buckets for  Push Message and Delivery Info buckets

zopsm_non_ttl_buckets for the rest of buckets

buckets_with_7d_ttl for zopsm_logs bucket
