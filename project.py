import argparse
from pathlib import Path
from loader import load_csv
from inference import infer_schema
from validators import check_missing_values, check_duplicates, check_type_anomalies
from reporting import build_report, format_summary, format_details, save_json


def main():
    parser = argparse.ArgumentParser(
        description="DataGuard — CSV Data Quality Analyzer"
    )
    parser.add_argument("path", help="Path to the CSV file")
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Show detailed report"
    )
    parser.add_argument("--json", help="Save report to JSON file")

    args = parser.parse_args()

    try:
        report = analyze_csv(args.path)
    except FileNotFoundError:
        parser.error(f"File '{args.path}' not found.")

    if args.json:
        if is_same_file(args.path, args.json):
            parser.error(f"Csv and json are reffering to the same file")
        try:
            save_json(report, args.json)
        except OSError as exc:
            parser.error(f"Failed to save JSON to '{args.json}': {exc}")

    if args.verbose:
        print(format_details(report))
    else:
        print(format_summary(report))


def analyze_csv(path: str) -> dict:
    data = load_csv(path)
    schema = infer_schema(data)
    checks = {
        "missing_values": check_missing_values(data),
        "duplicates": check_duplicates(data),
        "type_anomalies": check_type_anomalies(data, schema),
    }
    return build_report(data, schema, checks)


def is_same_file(csv_path: str, json_path: str) -> bool:
    csv_path_full = Path(csv_path).resolve()
    json_path_full = Path(json_path).resolve()
    if json_path_full.exists():
        return csv_path_full == json_path_full or csv_path_full.samefile(json_path_full)
    return csv_path_full == json_path_full


if __name__ == "__main__":
    main()
# python project.py data\test_loader.csv --json data\test_jsonnn
