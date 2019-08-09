#!/bin/bash
source venv/bin/activate
pytest -s -n auto -k 'stage and not hashes' --release=all