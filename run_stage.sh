#!/bin/bash
source venv/bin/activate
pytest -s -n auto --stage ./tests/test.py
