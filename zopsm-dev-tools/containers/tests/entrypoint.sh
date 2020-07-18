#!/usr/bin/env sh

# Write test data to Redis db=1
python -m zopsm.gateway.tests.prepare_test_data

# Run tests
pyresttest https://gw.zops.io /usr/local/lib/python3.6/site-packages/zopsm/gateway/tests/test_message.yaml