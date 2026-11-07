
import pandas as pd
from pathlib import Path
import json

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATASET_PATH = PROJECT_ROOT / "data" / "ManufacturingRCA_doc.csv"

REQUIRED_COLUMNS = [
    "Incident_ID",
    "Incident_Category",
    "Equipment",
    "Device",
    "Cause",
    "Immediate_Countermeasure",
    "Permanent_Countermeasure",
    "Location",
]


def load_dataset():
    """Load and validate the manufacturing incident dataset."""

    if not DATASET_PATH.exists():
        raise FileNotFoundError(f"Dataset not found: {DATASET_PATH}")

    df = pd.read_csv(DATASET_PATH)

    missing_columns = [
        column for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")

    print("Dataset loaded successfully!")
    print(f"Total incidents: {len(df)}")
    print(f"Total columns: {len(df.columns)}")

    return df


def clean_dataset(df):
    """Clean formatting inconsistencies in the dataset."""

    for column in df.select_dtypes(include=["object"]).columns:
        df[column] = df[column].str.strip()

    for column in ["Equipment", "Device"]:
        df[column] = df[column].str.strip('"').str.strip()

    df.replace(r"^\s*$", pd.NA, regex=True, inplace=True)

    print("\nDataset cleaning completed!")
    print(f"Remaining missing values: {df.isna().sum().sum()}")

    return df


def split_incident_details(df):
    """Split multiple causes and countermeasures into individual entries."""

    columns_to_split = [
        "Cause",
        "Immediate_Countermeasure",
        "Permanent_Countermeasure"
    ]

    for column in columns_to_split:
        df[column] = df[column].fillna("").apply(
            lambda value: [
                item.strip().strip("'- ")
                for item in value.split("<br>")
                if item.strip().strip("'- ")
            ]
        )

    print("\nIncident details separated successfully!")

    return df


def create_structured_records(df):
    """Convert incident data into structured records."""

    structured_records = []

    for _, row in df.iterrows():

        def get_text(column):
            value = row[column]

            if pd.isna(value):
                return None

            return str(value).strip()

        record = {
            "incident_id": get_text("Incident_ID"),
            "time": get_text("Time"),
            "discoverer": get_text("Discoverer"),
            "category": get_text("Incident_Category"),
            "summary": get_text("Incident_Summary"),
            "details": get_text("Detailed"),
            "impact_scope": get_text("Impact_Scope"),
            "equipment": get_text("Equipment"),
            "device": get_text("Device"),
            "location": get_text("Location"),
            "causes": row["Cause"],
            "immediate_actions": row["Immediate_Countermeasure"],
            "permanent_actions": row["Permanent_Countermeasure"]
        }

        structured_records.append(record)

    print("\nStructured records created successfully!")
    print("Total structured records:", len(structured_records))
    print("\nFirst structured record:")
    print(structured_records[0])

    return structured_records


def save_as_json(records):
    """Save structured incident records as a JSON file."""

    output_path = PROJECT_ROOT / "data" / "processed_incidents.json"

    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(records, file, indent=4, ensure_ascii=False)

    print("\nJSON file saved successfully!")
    print("Saved location:", output_path)


if __name__ == "__main__":
    df = load_dataset()
    df = clean_dataset(df)
    df = split_incident_details(df)
    records = create_structured_records(df)
    save_as_json(records)
