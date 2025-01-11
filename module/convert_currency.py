from dataclasses import dataclass


@dataclass
class ConvertCurrency:
    def toIDR(self, value: float) -> str:
        if value is None:
            return "Invalid value"

        try:
            return f"Rp. {int(value):,}".replace(",", ".")
        except (ValueError, TypeError):
            return "Invalid value"
