#!/usr/bin/env bash

systemctl stop riak || exit 1

EXIT_CODE=$?

sleep 10

if [[ "$EXIT_CODE" -eq 0 ]]; then

    DATE=`/bin/date +%Y%m%d_%H%M`

    /bin/mkdir -p /var/backups/riak/"$DATE"

    /bin/tar -czf /var/backups/riak/"$DATE"/riak_bitcask.tar.gz /var/lib/riak/bitcask /var/lib/riak/ring /etc/riak

    /bin/tar -czf /var/backups/riak/"$DATE"/riak_buckets_with_30d_ttl.tar.gz /var/lib/riak/buckets_with_30d_ttl /var/lib/riak/ring /etc/riak

    /bin/tar -czf /var/backups/riak/"$DATE"/riak_buckets_with_7d_ttl.tar.gz /var/lib/riak/buckets_with_7d_ttl /var/lib/riak/ring /etc/riak

    /bin/tar -czf /var/backups/riak/"$DATE"/riak_buckets_with_no_ttl.tar.gz /var/lib/riak/buckets_with_no_ttl /var/lib/riak/ring /etc/riak

    /bin/tar -czf /var/backups/riak/"$DATE"/riak_cluster_meta.tar.gz /var/lib/riak/cluster_meta

fi

until [[ $(/usr/sbin/riak ping) == "pong" ]]; do
   systemctl start riak
done