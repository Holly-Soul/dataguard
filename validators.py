from inference import (
    detect_value_type,
    is_type_compatible,
)


def check_missing_values(data: list[dict[str, str | None]]) -> dict:
    locations = []
    for index, dict_data in enumerate(data, start=1):
        for column_name, value in dict_data.items():
            if value in ("", None):
                locations.append({"row": index, "column": column_name})
    return {"count": len(locations), "locations": locations}


def check_duplicates(data: list[dict[str, str | None]]) -> dict:
    seen = set()
    locations = []

    for index, dict_data in enumerate(data, start=1):
        row_key = frozenset(dict_data.items())
        if row_key not in seen:
            seen.add(row_key)
        else:
            locations.append({"row": index, "column": None})

    return {"count": len(locations), "locations": locations}


def check_type_anomalies(data: list[dict[str, str | None]], schema: dict) -> dict:
    locations = []
    for row_number, row in enumerate(data, start=1):
        for column_name in schema:
            column_value = row.get(column_name)
            expected_type = schema[column_name]["inferred_type"]
            if (
                expected_type == "unknown"
                or column_value is None
                or column_value.strip() == ""
            ):
                continue
            if not is_type_compatible(expected_type, detect_value_type(column_value)):
                locations.append({"row": row_number, "column": column_name})
    return {
        "count": len(locations),
        "locations": locations,
    }


if __name__ == "__main__":
    ...
