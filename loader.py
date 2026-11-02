import csv


def load_csv(path: str) -> list[dict[str, str]]:
    with open(path, encoding="utf-8", newline="") as file:
        seen = set()
        rows = list()
        extra_key = object()
        data = csv.DictReader(file, restkey=extra_key)

        if data.fieldnames:
            column_names = data.fieldnames
        else:
            raise ValueError("CSV is empty")

        for column in column_names:
            if column not in seen:
                seen.add(column)
            else:
                raise ValueError(f"Duplicate column name: '{column}'")

        for row in data:
            if extra_key in row:
                raise ValueError(f"Extra values found at CSV line {data.line_num}")
            rows.append(row)

        return rows


if __name__ == "__main__":
    print(load_csv("data/test_loader.csv"))
    ...
