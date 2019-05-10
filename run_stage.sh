#!/bin/bash
source venv/bin/activate
STAGE_HOST=$(sh ./get_stage_host.sh)
STAGE_IP=$(sh ./get_ip.sh $STAGE_HOST)
pytest -s -n auto --stage --stageip=$STAGE_IP ./tests/test.py
