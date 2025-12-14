import re
from sklearn.preprocessing import LabelEncoder
import numpy as np  # linear algebra
import pandas as pd

# Because there are nearly 27 classes labeled in data set
# It should be efficient if same classes types combined
# the main are : [BENIGN, Portscan, DoS attack, Web Attack, ssh attack]


def merge_classes(datai):
    merge_map = {
        "BENIGN": "BENIGN",
        "Portscan": "Port Scanning",
        "Infiltration - Portscan": "Port Scanning",
        "DoS Hulk": "DoS",
        "DoS GoldenEye": "DoS",
        "DoS Slowloris": "DoS",
        "DoS Slowhttptest": "DoS",
        "DoS Hulk - Attempted": "DoS",
        "DoS GoldenEye - Attempted": "DoS",
        "DoS Slowloris - Attempted": "DoS",
        "DoS Slowhttptest - Attempted": "DoS",
        "DDoS": "DDoS",
        "Botnet": "Botnet",
        "Botnet - Attempted": "Botnet",
        "FTP-Patator": "FTP-Patator",
        "FTP-Patator - Attempted": "FTP-Patator",
        "SSH-Patator": "SSH-Patator",
        "SSH-Patator - Attempted": "SSH-Patator",
        "Web Attack - Brute Force": "Web Attacks",
        "Web Attack - Brute Force - Attempted": "Web Attacks",
        "Web Attack - XSS": "Web Attacks",
        "Web Attack - XSS - Attempted": "Web Attacks",
        "Web Attack - SQL Injection": "Web Attacks",
        "Web Attack - SQL Injection - Attempted": "Web Attacks",
        "Infiltration": "Infiltration",
        "Infiltration - Attempted": "Infiltration",
        "Heartbleed": "Heartbleed",
    }

    # Apply mapping to the Label column
    datai["Label"] = datai["Label"].map(merge_map)

    return datai


#### 1.
def has_missing_or_inf(datai):
    # Returns True if any value in the row is NaN or inf/-inf
    return datai.isnull().any().any() or np.isinf(datai.values).any()


###### 3
def extract_columns(text):
    with open(text, "r") as file:
        # Read lines from the file
        lines = file.readlines()
    # Extract column names, stripping newline characters
    columns = [line.strip() for line in lines]
    # print(columns)
    return columns


###### 4
def encoder(data, encoder):
    # Check for categorical columns
    categorical_columns = data.select_dtypes(include=["object", "string"]).columns
    # print(f"Categorical columns: {categorical_columns.tolist()}")

    # Encode categorical variables if any
    for col in categorical_columns:
        le = encoder
        data[col] = le.fit_transform(data[col].astype(str))
        # print(f"Encoded {col}")

    # Convert DataFrame back to dictionary
    return data.iloc[0].to_dict()


###### 5
def read_training_logs(text):
    with open(text, "r") as file:
        log = file.read()

    # print(log)

    # Pattern to capture all columns: epoch, loss, val_0_balanced_accuracy, val_0_accuracy, time
    pattern = re.compile(
        r"epoch\s+(\d+)\s*\|\s*loss:\s*([\d.]+)\s*\|\s*val_0_balanced_accuracy:\s*([\d.]+)\s*\|\s*val_0_accuracy:\s*([\d.]+)\s*\|\s*([\d:]+)s?"
    )

    results = []
    for match in re.finditer(pattern, log):
        epoch, loss, bal_acc, acc, time = match.groups()
        results.append(
            {
                "epoch": int(epoch),
                "loss": float(loss),
                "val_0_balanced_accuracy": float(bal_acc),
                "val_0_accuracy": float(acc),
                "time": time,
            }
        )

    return results  # Array of dictionaries containing training log details


##### 6
def read_columns(text):
    with open(text, "r") as file:
        text = file.read()
    # Split lines, strip whitespace, and remove empty lines
    columns = [line.strip() for line in text.strip().splitlines() if line.strip()]
    return columns  # return list of columns


def read_data_row(datai, index):
    if index < 0 or index >= len(datai):
        raise IndexError("Index out of bounds")
    return datai.iloc[index]
