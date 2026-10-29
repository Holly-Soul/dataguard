from loader import load_csv
from inference import infer_schema
from validators import check_missing_values, check_duplicates, check_type_anomalies
from reporting import build_report


def main():
    print(analyze_csv("data/test_loader.csv"))

def analyze_csv(path: str) -> dict:
    data = load_csv(path)
    schema = infer_schema(data)
    checks = {
        "missing_values": check_missing_values(data),
        "duplicates": check_duplicates(data),
        "type_anomalies": check_type_anomalies(data, schema),
        }
    return build_report(data, schema, checks)


if __name__ == "__main__":
    main()
