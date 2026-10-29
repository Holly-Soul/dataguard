import argparse
from loader import load_csv
from inference import infer_schema
from validators import check_missing_values, check_duplicates, check_type_anomalies
from reporting import build_report


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
    print(args.path)
    print(args.verbose)
    print(args.json)
    report = analyze_csv(args.path)
    print(report)


def analyze_csv(path: str) -> dict:
    data = load_csv(path)
    schema = infer_schema(data)
    checks = {
        "missing_values": check_missing_values(data),
        "duplicates": check_duplicates(data),
        "type_anomalies": check_type_anomalies(data, schema),
    }
    return build_report(data, schema, checks)


def format_summary(report: dict) -> str: ...


if __name__ == "__main__":
    main()
# python project.py data\test_loader.csv
