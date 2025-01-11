from dataclasses import dataclass
import random
from typing import Dict, Any, List
from module.loan_processor import LoanProcessor
from module.json import JsonHandler
from dataclasses import field


@dataclass
class LoanData:
    json_handler: JsonHandler = field(default_factory=JsonHandler)

    def generate(self, export_path: str) -> str:

        multiple_based_data_list = []
        for i in range(50):
            monthly_income = random.choice(
                [x * 1000000 for x in range(5, 21)]
                + [x * 150000 for x in range(35, 101)]
            )
            monthly_expenses = random.choice(
                [x * 1000000 for x in range(2, monthly_income // 1000000)]
                + [x * 150000 for x in range(15, monthly_income // 150000)]
            )
            requested_loan_amount = random.choice([x * 3000000 for x in range(3, 16)])
            collateral_estimate = random.choice(
                [
                    x * 1000000
                    for x in range(
                        int(requested_loan_amount * 0.8) // 1000000,
                        int(requested_loan_amount * 1.5) // 1000000,
                    )
                ]
            )

            employment_status = random.choice([True, False])
            previous_credit_history = random.choice([True, False])
            loan_term = random.randint(6, 36)

            data_entry = {
                "monthly_income": str(monthly_income),
                "monthly_expenses": str(monthly_expenses),
                "employment_status": employment_status,
                "previous_credit_history": previous_credit_history,
                "requested_loan_amount": str(requested_loan_amount),
                "collateral_estimate": str(collateral_estimate),
                "loan_term": loan_term,
                "customer_id": "cm57o3nos0000dijxyec3i3nx",
            }

            multiple_based_data_list.append(data_entry)

        self.json_handler.write_json(export_path, multiple_based_data_list)
        return export_path

    def update(
        self, import_file_path: str, export_file_path: str, interest_rate: float = 1.0
    ):

        data = self.json_handler.read_json(import_file_path)
        if data is None:
            return []

        updated_data = []
        processor = LoanProcessor()

        for entry in data:
            monthly_income = processor.safe_parse_number(entry.get("monthly_income"))
            monthly_expenses = processor.safe_parse_number(
                entry.get("monthly_expenses")
            )
            requested_loan_amount = processor.safe_parse_number(
                entry.get("requested_loan_amount")
            )
            loan_term = processor.safe_parse_number(entry.get("loan_term"))
            collateral_estimate = processor.safe_parse_number(
                entry.get("collateral_estimate")
            )

            monthly_surplus = monthly_income - monthly_expenses

            installment = processor.get_installment(
                requested_loan_amount, loan_term, interest_rate
            )
            credit_worthiness = processor.get_credit_worthiness(
                {
                    "requested_loan_amount": requested_loan_amount,
                    "collateral_estimate": collateral_estimate,
                    "monthly_surplus": monthly_surplus,
                    "installment": installment,
                    "employment_status": entry.get("employment_status"),
                    "previous_credit_history": entry.get("previous_credit_history"),
                }
            )

            entry["monthly_surplus"] = monthly_surplus
            entry["installment"] = installment
            entry["credit_worthiness"] = credit_worthiness

            updated_data.append(entry)

        self.json_handler.write_json(export_file_path, updated_data)

        return export_file_path
