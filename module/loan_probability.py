from module.json import JsonHandler
from module.loan_categorizer import LoanCategorizer
from dataclasses import field, dataclass


@dataclass
class LoanProbability:
    json_handler: JsonHandler = field(default_factory=JsonHandler)

    def calculate(self, file_path):
        categorizer = LoanCategorizer()
        data = self.json_handler.read_json(file_path)
        total_records = len(data)

        probabilities = {
            "overall": {},
            "conditional": {},
        }

        credit_worthy_count = sum(1 for record in data if record["credit_worthiness"])
        probabilities["credit_worthiness"] = {
            "true": {
                "fraction": f"{credit_worthy_count}/{total_records}",
                "percentage": f"{(credit_worthy_count/total_records)*100:.2f}%",
            },
            "false": {
                "fraction": f"{total_records - credit_worthy_count}/{total_records}",
                "percentage": f"{((total_records - credit_worthy_count)/total_records)*100:.2f}%",
            },
        }

        categories = {
            "employment_status": lambda x: str(x["employment_status"]).lower(),
            "monthly_income": lambda x: categorizer.categorize_income(
                x["monthly_income"]
            ),
            "expense_ratio": lambda x: categorizer.categorize_expenses(
                x["monthly_income"], x["monthly_expenses"]
            ),
            "surplus_ratio": lambda x: categorizer.categorize_surplus(
                x["monthly_income"], x["monthly_surplus"]
            ),
            "collateral": lambda x: categorizer.categorize_collateral(
                x["collateral_estimate"]
            ),
            "loan_term": lambda x: categorizer.categorize_loan_term(x["loan_term"]),
            "installment_vs_surplus": lambda x: categorizer.categorize_installment(
                x["installment"], x["monthly_surplus"]
            ),
            "loan_vs_collateral": lambda x: categorizer.categorize_loan_amount(
                x["requested_loan_amount"], x["collateral_estimate"]
            ),
            "previous_credit_history": lambda x: str(
                x["previous_credit_history"]
            ).lower(),
        }

        for category, func in categories.items():
            counts = {}
            for record in data:
                try:
                    value = func(record)
                    counts[value] = counts.get(value, 0) + 1
                except KeyError as e:
                    print(f"Warning: Missing key {e} in record for category {category}")
                    continue

            probabilities["overall"][category] = {
                value: {
                    "fraction": f"{count}/{total_records}",
                    "percentage": f"{(count/total_records)*100:.2f}%",
                }
                for value, count in counts.items()
            }

        for category, func in categories.items():
            probabilities["conditional"][category] = {}

            try:
                unique_values = set(func(record) for record in data)

                for value in unique_values:
                    credit_worthy_count = sum(
                        1
                        for record in data
                        if func(record) == value and record["credit_worthiness"]
                    )
                    total_value_count = sum(
                        1 for record in data if func(record) == value
                    )

                    if total_value_count > 0:
                        probabilities["conditional"][category][value] = {
                            "credit_worthy": {
                                "fraction": f"{credit_worthy_count}/{total_value_count}",
                                "percentage": f"{(credit_worthy_count/total_value_count)*100:.2f}%",
                            },
                            "not_credit_worthy": {
                                "fraction": f"{(total_value_count - credit_worthy_count)}/{total_value_count}",
                                "percentage": f"{((total_value_count - credit_worthy_count)/total_value_count)*100:.2f}%",
                            },
                        }
            except KeyError as e:
                print(f"Warning: Missing key {e} in record for category {category}")
                continue

        return probabilities

    def print_analysis_results(self, probabilities):
        if probabilities is None:
            print("Error: No data to analyze")
            return

        print("\n=== ANALISIS PROBABILITAS KREDIT ===")

        print("\nPROBABILITAS CREDIT WORTHINESS:")
        for value, probs in probabilities["credit_worthiness"].items():
            print(f"  {value}: {probs['fraction']} ({probs['percentage']})")

        print("\n1. PROBABILITAS KESELURUHAN:")
        for category, values in probabilities["overall"].items():
            print(f"\n{category.upper()}:")
            for value, probs in values.items():
                print(f"  {value}: {probs['fraction']} ({probs['percentage']})")

        print("\n2. PROBABILITAS KONDISIONAL BERDASARKAN CREDIT WORTHINESS:")
        for category, values in probabilities["conditional"].items():
            print(f"\n{category.upper()}:")
            for value, probs in values.items():
                print(f"  {value}:")
                print(
                    f"    Layak Kredit: {probs['credit_worthy']['fraction']} ({probs['credit_worthy']['percentage']})"
                )
                print(
                    f"    Tidak Layak: {probs['not_credit_worthy']['fraction']} ({probs['not_credit_worthy']['percentage']})"
                )
