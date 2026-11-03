import math
from collections import Counter
from datetime import date


# Type recognition
def detect_value_type(value: str) -> str:
    # bool
    if value.lower() in ("true", "false"):
        return "bool"
    # int
    try:
        int(value)
        if value == value.strip() and "_" not in value:
            return "int"
    except ValueError:
        pass
    # float
    try:
        float_check = float(value)
        if math.isfinite(float_check) and value == value.strip() and "_" not in value:
            return "float"
    except ValueError:
        pass
    # date
    if (
        len(value) == 10
        and value[4] == "-"
        and value[7] == "-"
        and value[0:4].isdigit()
        and value[5:7].isdigit()
        and value[8:10].isdigit()
    ):
        try:
            date.fromisoformat(value)
            return "date"
        except ValueError:
            pass
    # str
    return "str"


def infer_column_type(values: list[str | None]) -> dict:

    normalized_types = []

    detected_types = [
        detect_value_type(clear)
        for clear in values
        if clear is not None and clear.strip() != ""
    ]

    if not detected_types:
        return {"inferred_type": "unknown", "confidence": 0.0}

    if "float" in detected_types:
        for x in detected_types:
            if x == "int":
                normalized_types.append("float")
            else:
                normalized_types.append(x)
    else:
        normalized_types = detected_types

    counts = Counter(normalized_types)

    max_t, max_v = counts.most_common(1)[0]

    confidence = max_v / len(normalized_types)

    if confidence >= 0.8:
        inferred_type = max_t
    else:
        inferred_type = "unknown"

    return {"inferred_type": inferred_type, "confidence": round(confidence, 2)}


def infer_schema(data: list[dict[str, str | None]]) -> dict:

    # find unique keys
    seen = dict.fromkeys(key for row in data for key in row)

    # get full columns
    result = {}
    for key in seen:
        values = [row.get(key) for row in data]
        result[key] = infer_column_type(values)
    return result


def is_type_compatible(expected_type: str, actual_type: str) -> bool:
    return (
        (expected_type == "int" and actual_type == "int")
        or (expected_type == "float" and actual_type in ("int", "float"))
        or (expected_type == "bool" and actual_type == "bool")
        or (expected_type == "date" and actual_type == "date")
        or expected_type == "str"
    )


if __name__ == "__main__":
    ...
