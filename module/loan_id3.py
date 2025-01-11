import math
from dataclasses import dataclass, field
from typing import Dict, Any
from module.json import JsonHandler
from module.loan_categorizer import LoanCategorizer


@dataclass
class LoanID3:
    json_handler: JsonHandler = field(default_factory=JsonHandler)
    loan_categorizer: LoanCategorizer = field(default_factory=LoanCategorizer)

    def calculate_entropy(self, probabilities: list[float]) -> float:
        return -sum(p * math.log2(p) if p > 0 else 0 for p in probabilities)

    def calculate_entropy_gain(self, data: list[dict], attribute_func) -> dict:
        total_records = len(data)

        credit_worthy_count = sum(1 for record in data if record["credit_worthiness"])
        p_credit_worthy = credit_worthy_count / total_records
        p_not_credit_worthy = (total_records - credit_worthy_count) / total_records
        main_entropy = self.calculate_entropy([p_credit_worthy, p_not_credit_worthy])

        attribute_values = {}
        for record in data:
            value = attribute_func(record)
            if value not in attribute_values:
                attribute_values[value] = []
            attribute_values[value].append(record)

        weighted_entropy = 0
        value_probabilities = {}

        for value, subset in attribute_values.items():
            subset_size = len(subset)
            credit_worthy_subset = sum(
                1 for record in subset if record["credit_worthiness"]
            )
            p_credit_worthy_given_value = credit_worthy_subset / subset_size
            p_not_credit_worthy_given_value = (
                subset_size - credit_worthy_subset
            ) / subset_size

            subset_entropy = self.calculate_entropy(
                [p_credit_worthy_given_value, p_not_credit_worthy_given_value]
            )

            print(f"debug: {subset_entropy}")

            weighted_entropy += (subset_size / total_records) * subset_entropy

            value_probabilities[value] = {
                "subset_size": subset_size,
                "total_probability": f"{subset_size / total_records:.4f}",
                "credit_worthy_probability": f"{p_credit_worthy_given_value:.4f}",
                "not_credit_worthy_probability": f"{p_not_credit_worthy_given_value:.4f}",
                "entropy": f"{subset_entropy:.4f}",
            }

        information_gain = main_entropy - weighted_entropy

        return {
            "main_entropy": f"{main_entropy:.4f}",
            "weighted_entropy": f"{weighted_entropy:.4f}",
            "information_gain": f"{information_gain:.4f}",
            "value_probabilities": value_probabilities,
        }

    def analyze_credit_entropy(self, file_path: str) -> Dict[str, Any]:
        """Analyze entropy and information gain for all credit attributes"""
        data = self.json_handler.read_json(file_path)
        if data is None:
            return None

        categories = {
            "employment_status": lambda x: str(x["employment_status"]).lower(),
            "monthly_income": lambda x: self.loan_categorizer.categorize_income(
                x["monthly_income"]
            ),
            "expense_ratio": lambda x: self.loan_categorizer.categorize_expenses(
                x["monthly_expenses"], x["monthly_income"]
            ),
            "surplus_ratio": lambda x: self.loan_categorizer.categorize_surplus(
                x["monthly_surplus"], x["monthly_income"]
            ),
            "collateral": lambda x: self.loan_categorizer.categorize_collateral(
                x["collateral_estimate"]
            ),
            "loan_term": lambda x: self.loan_categorizer.categorize_loan_term(
                x["loan_term"]
            ),
            "installment_vs_surplus": lambda x: self.loan_categorizer.categorize_installment(
                x["installment"], x["monthly_surplus"]
            ),
            "loan_vs_collateral": lambda x: self.loan_categorizer.categorize_loan_amount(
                x["requested_loan_amount"], x["collateral_estimate"]
            ),
            "previous_credit_history": lambda x: str(
                x["previous_credit_history"]
            ).lower(),
        }

        results = {}
        for category, func in categories.items():
            results[category] = self.calculate_entropy_gain(data, func)

        return results

    def print_entropy_analysis(self, results: Dict[str, Any]) -> None:
        """Print entropy analysis results in a formatted way"""
        if results is None:
            return

        print("\n=== ANALISIS ENTROPI DAN GAIN KREDIT ===")

        sorted_attributes = sorted(
            results.items(), key=lambda x: float(x[1]["information_gain"]), reverse=True
        )

        for attribute, analysis in sorted_attributes:
            print(f"\n{attribute.upper()}:")
            print(f"  Entropi Utama: {analysis['main_entropy']}")
            print(f"  Entropi Berbobot: {analysis['weighted_entropy']}")
            print(f"  Information Gain: {analysis['information_gain']}")

            print("\n  Detail per nilai:")
            for value, probs in analysis["value_probabilities"].items():
                print(f"    {value}:")
                print(f"      Probabilitas Total: {probs['total_probability']}")
                print(
                    f"      Probabilitas Layak Kredit: {probs['credit_worthy_probability']}"
                )
                print(
                    f"      Probabilitas Tidak Layak: {probs['not_credit_worthy_probability']}"
                )
                print(f"      Entropi: {probs['entropy']}")
