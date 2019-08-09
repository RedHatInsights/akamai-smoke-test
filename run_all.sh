#!/bin/bash
source venv/bin/activate
pytest -s -n auto -k '(stage or prod) and (beta or stable) and not hashes' --release=all
