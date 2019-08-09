#!/bin/bash
source venv/bin/activate
pytest --capture=sys -n auto -k 'prod and not hashes' --release=all
