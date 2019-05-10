#!/bin/bash
source venv/bin/activate
PROD_HOST='cloud.redhat.com'
PROD_IP=$(sh ./get_ip.sh $PROD_HOST)
pytest -s -n auto --prod --prodip=$PROD_IP ./tests/test.py
