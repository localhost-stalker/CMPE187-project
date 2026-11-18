import argparse
import csv
from collections import Counter, defaultdict
from pathlib import Path

from config import RESULTS_DIR


RESULT_LABELS = ("Pass", "Partial Pass", "Fail", "Error")
REQUIRED_COLUMNS = {
    "test_id",
    "test_name",
    "model",
    "result",
    "response_time_seconds",
}
SUMMARY_COLUMNS = [
    "scope",
    "model",
    "test_id",
    "test_name",
    "total",
    "pass_count",
    "partial_pass_count",
    "fail_count",
    "error_count",
    "strict_pass_rate",
    "pass_or_partial_rate",
    "average_response_time_seconds",
]


def parse_args():
    parser = argparse.ArgumentParser(
        description="Summarize a CMPE 187 audio automation results CSV."
    )
    parser.add_argument(
        "--input",
        type=Path,
        help="Path to a combined_results CSV. Defaults to the newest file in results/.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Path for the analysis summary CSV. Defaults beside the input CSV.",
    )
    parser.add_argument(
        "--charts",
        action="store_true",
        help="Also save model-summary charts (requires matplotlib).",
    )
    return parser.parse_args()


def latest_results_file():
    candidates = list(RESULTS_DIR.glob("combined_results_*.csv"))
    if not candidates:
        raise FileNotFoundError(
            "No combined results CSV was found. Run run_tests.py first or pass --input PATH."
        )
    return max(candidates, key=lambda path: path.stat().st_mtime)


def read_results(input_path):
    if not input_path.is_file():
        raise FileNotFoundError(f"Results CSV not found: {input_path}")

    with input_path.open(newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        fieldnames = set(reader.fieldnames or [])
        missing_columns = REQUIRED_COLUMNS - fieldnames
        if missing_columns:
            raise ValueError(
                "Results CSV is missing required column(s): "
                f"{', '.join(sorted(missing_columns))}"
            )

        rows = []
        for line_number, row in enumerate(reader, start=2):
            result = (row.get("result") or "").strip()
            if result not in RESULT_LABELS:
                raise ValueError(
                    f"Row {line_number} has an unknown result label: {result!r}"
                )

            elapsed_text = (row.get("response_time_seconds") or "").strip()
            try:
                elapsed = float(elapsed_text) if elapsed_text else None
            except ValueError as exc:
                raise ValueError(
                    f"Row {line_number} has an invalid response time: {elapsed_text!r}"
                ) from exc

            rows.append(
                {
                    "test_id": (row.get("test_id") or "").strip(),
                    "test_name": (row.get("test_name") or "").strip(),
                    "model": (row.get("model") or "").strip(),
                    "result": result,
                    "response_time_seconds": elapsed,
                }
            )

    if not rows:
        raise ValueError("Results CSV contains no test rows.")
    return rows


def calculate_metrics(rows):
    counts = Counter(row["result"] for row in rows)
    times = [
        row["response_time_seconds"]
        for row in rows
        if row["response_time_seconds"] is not None
    ]
    total = len(rows)

    return {
        "total": total,
        "pass_count": counts["Pass"],
        "partial_pass_count": counts["Partial Pass"],
        "fail_count": counts["Fail"],
        "error_count": counts["Error"],
        "strict_pass_rate": counts["Pass"] / total,
        "pass_or_partial_rate": (counts["Pass"] + counts["Partial Pass"]) / total,
        "average_response_time_seconds": sum(times) / len(times) if times else None,
    }


def group_rows(rows, key_function):
    groups = defaultdict(list)
    for row in rows:
        groups[key_function(row)].append(row)
    return groups


def summary_row(scope, rows, model="", test_id="", test_name=""):
    metrics = calculate_metrics(rows)
    return {
        "scope": scope,
        "model": model,
        "test_id": test_id,
        "test_name": test_name,
        **metrics,
    }


def build_summary(rows):
    summary = [summary_row("overall", rows)]

    by_model = group_rows(rows, lambda row: row["model"])
    for model, group in sorted(by_model.items()):
        summary.append(summary_row("model", group, model=model))

    by_test = group_rows(rows, lambda row: (row["test_id"], row["test_name"]))
    for (test_id, test_name), group in sorted(by_test.items()):
        summary.append(summary_row("test", group, test_id=test_id, test_name=test_name))

    by_model_test = group_rows(
        rows, lambda row: (row["model"], row["test_id"], row["test_name"])
    )
    for (model, test_id, test_name), group in sorted(by_model_test.items()):
        summary.append(
            summary_row(
                "model_test",
                group,
                model=model,
                test_id=test_id,
                test_name=test_name,
            )
        )

    return summary


def write_summary(summary, output_path):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=SUMMARY_COLUMNS)
        writer.writeheader()
        for row in summary:
            writer.writerow(
                {
                    **row,
                    "strict_pass_rate": f"{row['strict_pass_rate']:.4f}",
                    "pass_or_partial_rate": f"{row['pass_or_partial_rate']:.4f}",
                    "average_response_time_seconds": (
                        f"{row['average_response_time_seconds']:.2f}"
                        if row["average_response_time_seconds"] is not None
                        else ""
                    ),
                }
            )


def print_metrics(title, row):
    average_time = row["average_response_time_seconds"]
    average_time_text = f"{average_time:.2f} sec" if average_time is not None else "n/a"

    print(f"\n{title}")
    print(f"  Total: {row['total']}")
    print(
        "  Results: "
        f"Pass {row['pass_count']} | "
        f"Partial Pass {row['partial_pass_count']} | "
        f"Fail {row['fail_count']} | "
        f"Error {row['error_count']}"
    )
    print(f"  Strict pass rate: {row['strict_pass_rate']:.1%}")
    print(f"  Pass or partial rate: {row['pass_or_partial_rate']:.1%}")
    print(f"  Average response time: {average_time_text}")


def print_summary(summary):
    print("=== Results Analysis ===")
    print_metrics("Overall", summary[0])

    print("\nPer model")
    for row in (item for item in summary if item["scope"] == "model"):
        print_metrics(row["model"], row)

    print("\nPer test")
    for row in (item for item in summary if item["scope"] == "test"):
        print_metrics(f"{row['test_id']} - {row['test_name']}", row)


def create_charts(summary, output_path):
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("Charts skipped: install matplotlib with 'python -m pip install matplotlib'.")
        return []

    model_rows = [row for row in summary if row["scope"] == "model"]
    if not model_rows:
        return []

    models = [row["model"] for row in model_rows]
    chart_path = output_path.with_name(f"{output_path.stem}_models.png")
    figure, (counts_axis, rate_axis) = plt.subplots(1, 2, figsize=(13, 5))

    bottom = [0] * len(model_rows)
    colors = {"Pass": "#2e7d32", "Partial Pass": "#f9a825", "Fail": "#c62828", "Error": "#6d6d6d"}
    fields = {
        "Pass": "pass_count",
        "Partial Pass": "partial_pass_count",
        "Fail": "fail_count",
        "Error": "error_count",
    }
    for label in RESULT_LABELS:
        values = [row[fields[label]] for row in model_rows]
        counts_axis.bar(models, values, bottom=bottom, label=label, color=colors[label])
        bottom = [total + value for total, value in zip(bottom, values)]

    counts_axis.set_title("Results by model")
    counts_axis.set_ylabel("Test executions")
    counts_axis.tick_params(axis="x", rotation=25)
    counts_axis.legend()

    pass_rates = [row["strict_pass_rate"] * 100 for row in model_rows]
    acceptable_rates = [row["pass_or_partial_rate"] * 100 for row in model_rows]
    positions = list(range(len(model_rows)))
    rate_axis.bar(positions, pass_rates, label="Pass", color="#2e7d32")
    rate_axis.bar(
        positions,
        [acceptable - strict for acceptable, strict in zip(acceptable_rates, pass_rates)],
        bottom=pass_rates,
        label="Partial Pass",
        color="#f9a825",
    )
    rate_axis.set_title("Pass rates by model")
    rate_axis.set_ylabel("Percent of test executions")
    rate_axis.set_ylim(0, 100)
    rate_axis.set_xticks(positions, models, rotation=25, ha="right")
    rate_axis.legend()

    figure.tight_layout()
    figure.savefig(chart_path, dpi=180)
    plt.close(figure)
    return [chart_path]


def main():
    args = parse_args()
    try:
        input_path = args.input or latest_results_file()
        rows = read_results(input_path)
    except (FileNotFoundError, ValueError, csv.Error) as exc:
        raise SystemExit(f"Error: {exc}") from exc

    summary = build_summary(rows)

    output_path = args.output or input_path.with_name(f"analysis_{input_path.name}")
    write_summary(summary, output_path)
    print_summary(summary)
    print(f"\nAnalysis CSV saved to: {output_path}")

    for chart_path in create_charts(summary, output_path) if args.charts else []:
        print(f"Chart saved to: {chart_path}")


if __name__ == "__main__":
    main()
