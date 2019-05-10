#!/bin/bash
source venv/bin/activate
STAGE_HOST=$(sh ./get_stage_host.sh)
STAGE_IP=$(sh ./get_ip.sh $STAGE_HOST)
PROD_HOST='cloud.redhat.com'
PROD_IP=$(sh ./get_ip.sh $PROD_HOST)

pytest -s -n auto --prod --prodip=$PROD_IP --stage --stageip=$STAGE_IP ./tests/test.py
