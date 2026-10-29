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


if __name__ == "__main__":
    ...
