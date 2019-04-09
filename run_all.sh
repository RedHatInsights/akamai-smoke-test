#!/bin/bash
source venv/bin/activate
pytest -s -n auto --prod --stage ./tests/test.py
