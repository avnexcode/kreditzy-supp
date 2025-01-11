from dataclasses import dataclass, field
import math
from typing import Dict, Any, List


@dataclass
class LoanProcessor:
    def safe_parse_number(self, value: Any) -> float:
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0

    def get_installment(
        self, requested_loan_amount: float, loan_term: int, interest_rate: float = 1
    ) -> str:
        loan_amount = self.safe_parse_number(requested_loan_amount)
        term = self.safe_parse_number(loan_term)
        rate = self.safe_parse_number(interest_rate) / 100

        if term == 0:
            raise ValueError("Loan term must be greater than zero.")

        base_installment = loan_amount / term
        interest_amount = loan_amount * rate
        total_installment = math.ceil((base_installment + interest_amount) / 100) * 100

        return f"{total_installment}"

    def get_credit_worthiness(self, loan_data: Dict[str, Any]) -> bool:
        loan_amount = self.safe_parse_number(loan_data.get("requested_loan_amount"))
        collateral = self.safe_parse_number(loan_data.get("collateral_estimate"))
        surplus = self.safe_parse_number(loan_data.get("monthly_surplus"))
        monthly_installment = self.safe_parse_number(loan_data.get("installment"))

        if loan_amount > collateral:
            if not loan_data.get("previous_credit_history", False):
                return False
            if not loan_data.get("employment_status", False):
                return False

        if surplus <= 0:
            return False

        if monthly_installment > surplus:
            return False

        return True
