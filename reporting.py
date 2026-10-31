from inference import infer_schema
from validators import check_missing_values, check_duplicates, check_type_anomalies


def build_report(
    data: list[dict[str, str | None]],
    schema: dict,
    checks: dict,
) -> dict:
    # 1. Calculate summary
    total_rows = len(data)
    total_columns = len(schema)
    total_issues = sum(counts["count"] for counts in checks.values())

    summary = {
        "total_rows": total_rows,
        "total_columns": total_columns,
        "total_issues": total_issues,
    }
    # 2. Return report
    return {"summary": summary, "schema": schema, "checks": checks}


def format_summary(report: dict) -> str:
    rows_analyzed_value = report["summary"]["total_rows"]
    columns_analyzed_value = report["summary"]["total_columns"]
    total_issues_value = report["summary"]["total_issues"]

    total_missing_value = report["checks"]["missing_values"]["count"]
    total_duplicates_value = report["checks"]["duplicates"]["count"]
    total_type_anomalies_value = report["checks"]["type_anomalies"]["count"]

    return (
        f"{"="*40}\n{"DATAGUARD REPORT":^40}\n{"="*40}\n\n"
        f"{"Rows analyzed:":<22}{rows_analyzed_value:>6}\n"
        f"{"Columns analyzed:":<22}{columns_analyzed_value:>6}\n"
        f"{"Total issues:":<22}{total_issues_value:>6}\n\n"
        f"{"-"*40}\n{"ISSUES SUMMARY":^40}\n{"-"*40}\n\n"
        f"{"Missing values:":<22}{total_missing_value:>6}\n"
        f"{"Duplicate rows:":<22}{total_duplicates_value:>6}\n"
        f"{"Type anomalies:":<22}{total_type_anomalies_value:>6}\n"
    )


def format_details(report: dict) -> str: ...


if __name__ == "__main__":
    ...
