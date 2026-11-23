# CMPE 187 Audio Test Automation

This project runs the same eight audio test cases through multiple AI-model adapters
and grades every response with the same deterministic grading rules.

## Setup

1. Create a virtual environment. Python 3.12 is required to run Nvidia Canary-Qwen 2.5B

   python -3.12 -m venv .venv

2. Install dependencies:

   pip install -r requirements.txt

3. Copy `.env.example` to `.env` and add your API keys.

## Run selected models

    python run_tests.py --models gpt

## Run selected tests

    python run_tests.py --models gpt --tests T1 T3 T8

## Run all configured models

    python run_tests.py --models all

## Analyze results

Analyze the newest test-run CSV automatically:

    python analyze_results.py

Analyze a specific run or also create charts (charts require `matplotlib`):

    python analyze_results.py --input results/combined_results_YYYYMMDD_HHMMSS.csv
    
    python analyze_results.py --charts

The analyzer prints overall, per-model, and per-test results. It also saves a
summary CSV beside the input file.

## Project structure

- `run_tests.py` - one main runner for every model
- `analyze_results.py` - summary statistics and optional charts for test runs
- `tests.py` - the eight shared test definitions and expected results
- `graders.py` - Pass / Partial Pass / Fail evaluation logic
- `models/` - one adapter per AI model
- `audio/` - original test audio
- `results/` - combined CSV result files
- `augmentation/` - data-augmentation work for Deliverable #3

## Result format

Each automated execution records:
- model
- test ID and name
- audio file
- expected result
- model response
- Pass / Partial Pass / Fail
- response time
- error, if any

