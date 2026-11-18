import argparse
import csv
import time
from datetime import datetime

from dotenv import load_dotenv

from config import BASE_DIR, AUDIO_DIR, RESULTS_DIR
from graders import grade_response
from models import get_model_adapters
from tests import TESTS


load_dotenv(BASE_DIR / ".env")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Run the CMPE 187 audio test suite on one or more AI models."
    )
    parser.add_argument(
        "--models",
        nargs="+",
        default=["gpt"],
        help="Models to run: gpt gemini qwen2 canary, or 'all'. Default: gpt",
    )
    parser.add_argument(
        "--tests",
        nargs="+",
        help="Optional test IDs to run, for example: --tests T1 T3 T8",
    )
    return parser.parse_args()


def selected_models(requested, adapters):
    if "all" in requested:
        return list(adapters.keys())

    unknown = [name for name in requested if name not in adapters]
    if unknown:
        raise ValueError(
            f"Unknown model(s): {', '.join(unknown)}. "
            f"Available: {', '.join(adapters.keys())}"
        )
    return requested


def selected_tests(test_ids):
    if not test_ids:
        return TESTS

    wanted = {test_id.upper() for test_id in test_ids}
    chosen = [test for test in TESTS if test["id"].upper() in wanted]
    missing = wanted - {test["id"].upper() for test in chosen}
    if missing:
        raise ValueError(f"Unknown test ID(s): {', '.join(sorted(missing))}")
    return chosen


def run_one(adapter, test):
    audio_path = AUDIO_DIR / test["audio"]
    if not audio_path.exists():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    start = time.perf_counter()
    response = adapter.run(audio_path, test["prompt"])
    elapsed = time.perf_counter() - start

    grade = grade_response(test, response)

    return {
        "test_id": test["id"],
        "test_name": test["name"],
        "model": adapter.display_name,
        "audio_file": test["audio"],
        "expected": test["expected"],
        "actual_response": response,
        "result": grade,
        "response_time_seconds": f"{elapsed:.2f}",
        "error": "",
    }


def save_results(results):
    RESULTS_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = RESULTS_DIR / f"combined_results_{timestamp}.csv"

    fieldnames = [
        "test_id",
        "test_name",
        "model",
        "audio_file",
        "expected",
        "actual_response",
        "result",
        "response_time_seconds",
        "error",
    ]

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    return output_path


def print_summary(results):
    print("\n=== Automation Summary ===")

    models = sorted({row["model"] for row in results})
    for model in models:
        rows = [row for row in results if row["model"] == model]
        counts = {}
        times = []

        for row in rows:
            counts[row["result"]] = counts.get(row["result"], 0) + 1
            if row["response_time_seconds"]:
                times.append(float(row["response_time_seconds"]))

        print(f"\n{model}")
        print(f"  Total: {len(rows)}")
        for label in ["Pass", "Partial Pass", "Fail", "Error"]:
            print(f"  {label}: {counts.get(label, 0)}")
        if times:
            print(f"  Average response time: {sum(times) / len(times):.2f} seconds")


def main():
    args = parse_args()
    adapters = get_model_adapters()
    model_keys = selected_models(args.models, adapters)
    tests = selected_tests(args.tests)

    results = []

    for model_key in model_keys:
        adapter = adapters[model_key]

        print(f"\n=== {adapter.display_name} ===")

        if not adapter.is_configured():
            print(f"Skipped: {adapter.configuration_help()}")
            continue

        for index, test in enumerate(tests, start=1):
            print(f"[{index}/{len(tests)}] {test['id']} - {test['name']}")

            try:
                row = run_one(adapter, test)
                print(f"  Result: {row['result']}")
                print(f"  Time: {row['response_time_seconds']} sec")
                print(f"  Response: {row['actual_response']}\n")
            except Exception as exc:
                row = {
                    "test_id": test["id"],
                    "test_name": test["name"],
                    "model": adapter.display_name,
                    "audio_file": test["audio"],
                    "expected": test["expected"],
                    "actual_response": "",
                    "result": "Error",
                    "response_time_seconds": "",
                    "error": str(exc),
                }
                print(f"  Error: {exc}\n")

            results.append(row)

    if not results:
        print("\nNo configured models were executed.")
        return

    output_path = save_results(results)
    print_summary(results)
    print(f"\nResults saved to: {output_path}")


if __name__ == "__main__":
    main()
