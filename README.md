# CMPE 187 Audio Test Automation

This project runs the same eight audio test cases through multiple AI-model adapters
and grades every response with the same deterministic grading rules.

## Setup

1. Create a virtual environment.
2. Install dependencies:

   pip install -r requirements.txt

3. Copy `.env.example` to `.env` and add your API keys.

## Run selected models

    python run_tests.py --models gpt

## Run selected tests

    python run_tests.py --models gpt --tests T1 T3 T8

## Run all configured models

    python run_tests.py --models all

## Project structure

- `run_tests.py` - one main runner for every model
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

