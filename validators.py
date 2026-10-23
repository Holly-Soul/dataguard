def check_missing_values(data: list[dict[str, str | None]]) -> dict:
    missing_report = {}
    locations = []
    for index, dict_data in enumerate(data, start=1):
        for column_name, value in dict_data.items():
            if value in ("", None):
                locations.append({"row": index, "column": column_name})
    missing_report["count"] = len(locations)
    missing_report["locations"] = locations
    return missing_report

print(check_missing_values([
        {"id": "1", "name": ""},
        {"id": "2", "name": "Maria"},
        {"id": "3", "name": None},
        {"id": "4", "name": "", "age": None}
    ]))
if __name__ == "__main__":
    True
