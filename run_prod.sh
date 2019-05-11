#!/bin/bash
source venv/bin/activate
pytest -s -n auto --prod ./tests/test.py
