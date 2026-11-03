import argparse
from pathlib import Path

from inference import infer_schema
from loader import load_csv
from reporting import build_report, format_details, format_summary, save_json
from validators import check_duplicates, check_missing_values, check_type_anomalies


def main():

    parser = create_parser()
    args = parser.parse_args()

    try:
        report = analyze_csv(args.path)
    except UnicodeDecodeError:
        parser.error("Unable to decode CSV. Expected UTF-8 encoding.")
    except FileNotFoundError:
        parser.error(f"File '{args.path}' not found.")
    except ValueError as exc:
        parser.error(str(exc))

    if args.json:
        if is_same_file(args.path, args.json):
            parser.error("Input CSV and output JSON refer to the same file")
        try:
            save_json(report, args.json)
        except OSError as exc:
            parser.error(f"Failed to save JSON to '{args.json}': {exc!s}")

    if args.verbose:
        print(format_details(report))
    else:
        print(format_summary(report))


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="DataGuard — CSV Data Quality Analyzer"
    )

    parser.add_argument("path", help="Path to the CSV file")

    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Show detailed report"
    )

    parser.add_argument("--json", help="Save report to JSON file")

    return parser


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
