#!/bin/bash
source venv/bin/activate
pytest -sv -n auto ./test/test.py
