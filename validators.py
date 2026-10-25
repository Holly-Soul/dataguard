from loader import load_csv


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


if __name__ == "__main__":
    data = load_csv("data/test_loader.csv")
    print("Nulls: ", check_missing_values(data))
    print(
        "Dubls: ",
        check_duplicates([{"id": "1", "name": "Alex"}, {"id": "Alex", "name": "1"}]),
    )
