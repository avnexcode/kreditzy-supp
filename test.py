import json
import math
from typing import List, Dict, Any
from pprint import pprint


def load_data(file_path: str) -> List[Dict[str, Any]]:
    try:
        with open(file_path, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Error: File {file_path} not found")
        return []
    except json.JSONDecodeError:
        print(f"Error: File {file_path} contains invalid JSON")
        return []


def calculate_entropy(
    data: List[Dict[str, Any]], target_attr: str = "credit_worthiness"
) -> float:
    if not data:
        return 0.0

    value_counts = {}
    total = len(data)

    for item in data:
        value = item[target_attr]
        value_counts[value] = value_counts.get(value, 0) + 1

    entropy = 0.0
    for count in value_counts.values():
        probability = count / total
        if probability > 0:
            entropy -= probability * math.log2(probability)

    return entropy


def split_data(
    data: List[Dict[str, Any]], attribute: str
) -> Dict[str, List[Dict[str, Any]]]:
    splits = {}

    if attribute == "installment_vs_surplus":
        for item in data:
            installment = float(item["installment"])
            surplus = float(item["monthly_surplus"])
            value = (
                "installment <= surplus"
                if installment <= surplus
                else "installment > surplus"
            )
            splits.setdefault(value, []).append(item)

    elif attribute == "loan_vs_collateral":
        for item in data:
            loan = float(item["requested_loan_amount"])
            collateral = float(item["collateral_estimate"])
            value = (
                "requested <= collateral"
                if loan <= collateral
                else "requested > collateral"
            )
            splits.setdefault(value, []).append(item)

    elif attribute == "employment_status":
        for item in data:
            value = "tetap" if item["employment_status"] else "tidak tetap"
            splits.setdefault(value, []).append(item)

    elif attribute == "previous_credit_history":
        for item in data:
            value = "baik" if item["previous_credit_history"] else "buruk"
            splits.setdefault(value, []).append(item)

    return splits


def calculate_gain(data: List[Dict[str, Any]], attribute: str) -> float:

    system_entropy = calculate_entropy(data)
    print(f"\nSystem entropy for {attribute}: {system_entropy:.6f}")

    splits = split_data(data, attribute)

    weighted_entropy = 0.0
    total_size = len(data)

    print("\nSplit details:")
    for value, subset in splits.items():
        subset_size = len(subset)
        subset_entropy = calculate_entropy(subset)
        weight = subset_size / total_size
        contribution = weight * subset_entropy
        weighted_entropy += contribution

        print(f"Split '{value}':")
        print(f"  Size: {subset_size}")
        print(f"  Total: {total_size}")
        print(f"  Weight (|Sv|/|S|): {weight:.6f}")
        print(f"  Subset Entropy: {subset_entropy:.6f}")
        print(f"  Weighted entropy: {weighted_entropy:.6f}")
        print(f"  Contribution to weighted entropy: {contribution:.6f}")

    gain = system_entropy - weighted_entropy
    return gain


def analyze_credit_attributes(data: List[Dict[str, Any]]) -> Dict[str, float]:
    attributes = [
        "installment_vs_surplus",
        "loan_vs_collateral",
        "employment_status",
        "previous_credit_history",
    ]

    gains = {}
    print("\nDetailed Gain Calculations:")
    print("=" * 60)

    for attr in attributes:
        print(f"\nCalculating gain for: {attr}")
        print("-" * 60)
        gains[attr] = calculate_gain(data, attr)
        print(f"Final Information Gain: {gains[attr]:.6f}")

    return gains


def main():

    file_path = "./data/json/final.json"
    data = load_data(file_path)

    if not data:
        print("No data to process")
        return

    print(f"Loaded {len(data)} records from {file_path}")

    gains = analyze_credit_attributes(data)

    print("\nFinal Information Gains Summary:")
    print("=" * 60)
    for attr, gain in gains.items():
        print(f"{attr:30} : {gain:.6f}")


if __name__ == "__main__":
    main()
