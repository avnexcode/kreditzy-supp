from dataclasses import dataclass
from typing import Union


@dataclass
class LoanCategorizer:
    def categorize_income(self, income: Union[str, float, int]) -> str:
        income = float(income)
        if income < 5_000_000:
            return "Rendah"
        elif income <= 8_000_000:
            return "Sedang"
        return "Tinggi"

    def categorize_expenses(
        self, expenses: Union[str, float, int], income: Union[str, float, int]
    ) -> str:
        ratio = float(expenses) / float(income)
        if ratio <= 0.7:
            return "Rendah"
        elif ratio <= 0.8:
            return "Sedang"
        return "Tinggi"

    def categorize_surplus(
        self, surplus: Union[str, float, int], income: Union[str, float, int]
    ) -> str:
        ratio = float(surplus) / float(income)
        if ratio >= 0.3:
            return "Tinggi"
        elif ratio >= 0.2:
            return "Sedang"
        return "Rendah"

    def categorize_collateral(self, collateral: Union[str, float, int]) -> str:
        collateral = float(collateral)
        if collateral < 10_000_000:
            return "Rendah"
        elif collateral <= 20_000_000:
            return "Sedang"
        return "Tinggi"

    def categorize_loan_term(self, term: Union[str, int]) -> str:
        term = int(term)
        if term < 12:
            return "Pendek"
        elif term <= 24:
            return "Sedang"
        return "Panjang"

    def categorize_installment(
        self, installment: Union[str, float, int], surplus: Union[str, float, int]
    ) -> str:
        return "<= Surplus" if float(installment) <= float(surplus) else "> Surplus"

    def categorize_loan_amount(
        self,
        loan_amount: Union[str, float, int],
        collateral_estimate: Union[str, float, int],
    ) -> str:
        return (
            "<= Taksiran Jaminan"
            if float(loan_amount) <= float(collateral_estimate)
            else "> Taksiran Jaminan"
        )
