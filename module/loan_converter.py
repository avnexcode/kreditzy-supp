import pandas as pd
from cuid import cuid
from dataclasses import field, dataclass
from datetime import datetime
from typing import List
from module.json import JsonHandler
from module.loan_categorizer import LoanCategorizer
from module.convert_currency import ConvertCurrency


@dataclass
class LoanConverter:
    json_handler: JsonHandler = field(default_factory=JsonHandler)
    convert_currency: ConvertCurrency = field(default_factory=ConvertCurrency)
    loan_categorizer: LoanCategorizer = field(default_factory=LoanCategorizer)

    def _convert_numeric_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        numeric_columns = [
            "monthly_income",
            "monthly_expenses",
            "monthly_surplus",
            "requested_loan_amount",
            "collateral_estimate",
            "installment",
        ]
        for col in numeric_columns:
            df[col] = df[col].astype(float)
        df["loan_term"] = df["loan_term"].astype(int)
        return df

    def _rename_and_order_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        column_order = [
            "Pendapatan",
            "Pengeluaran",
            "Jumlah Pinjaman",
            "Total Jaminan",
            "Surplus",
            "Angsuran",
            "Status Pekerjaan",
            "Riwayat Kredit",
            "Jangka Waktu",
            "Kelayakan",
        ]
        return df[column_order]

    def generate_cuid(self) -> str:
        return cuid()

    def _generate_sql_statement(self, entry: dict) -> str:
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        random_id = self.generate_cuid()

        return f"""
        INSERT INTO loan_references (
            id, monthly_income, monthly_expenses, monthly_surplus, employment_status,
            previous_credit_history, requested_loan_amount, collateral_estimate,
            loan_term, installment, customer_id, created_at, updated_at, credit_worthiness
        ) VALUES (
            '{random_id}', '{entry["monthly_income"]}', '{entry["monthly_expenses"]}', '{entry["monthly_surplus"]}', 
            {str(entry["employment_status"]).lower()}, {str(entry["previous_credit_history"]).lower()}, 
            '{entry["requested_loan_amount"]}', '{entry["collateral_estimate"]}', {entry["loan_term"]}, 
            '{entry["installment"]}', '{entry["customer_id"]}', '{created_at}', '{created_at}', 
            {str(entry["credit_worthiness"]).lower()}
        );
        """

    def json_to_sql(self, import_file: str, export_file: str) -> str:
        data = self.json_handler.read_json(import_file)
        sql_statements = []
        for entry in data:
            sql_statement = self._generate_sql_statement(entry)
            sql_statements.append(sql_statement)

        try:
            with open(export_file, "w") as file:
                file.write("\n".join(sql_statements))
            print(f"SQL file generated successfully: {export_file}")
            return export_file
        except Exception as e:
            raise ValueError(f"Error writing SQL file: {str(e)}")

    def json_to_excel(self, import_file: str, export_file: str) -> str:
        data = self.json_handler.read_json(import_file)
        if data is None:
            raise ValueError(f"Could not read data from {import_file}")

        df = pd.DataFrame(data)
        if df.empty:
            raise ValueError("DataFrame is empty. Please provide valid input data.")

        df = self._convert_numeric_columns(df)
        result_df = pd.DataFrame()

        result_df["Pendapatan"] = df["monthly_income"].apply(
            lambda x: self.convert_currency.toIDR(x)
        )
        result_df["Pengeluaran"] = df["monthly_expenses"].apply(
            lambda x: self.convert_currency.toIDR(x)
        )
        result_df["Jumlah Pinjaman"] = df["requested_loan_amount"].apply(
            lambda x: self.convert_currency.toIDR(x)
        )
        result_df["Total Jaminan"] = df["collateral_estimate"].apply(
            lambda x: self.convert_currency.toIDR(x)
        )
        result_df["Surplus"] = df["monthly_surplus"].apply(
            lambda x: self.convert_currency.toIDR(x)
        )
        result_df["Angsuran"] = df["installment"].apply(
            lambda x: self.convert_currency.toIDR(x)
        )

        result_df["Status Pekerjaan"] = df["employment_status"].map(
            {True: "Tetap", False: "Tidak Tetap"}
        )
        result_df["Riwayat Kredit"] = df["previous_credit_history"].map(
            {True: "Baik", False: "Buruk"}
        )
        result_df["Jangka Waktu"] = df["loan_term"].astype(str) + " months"
        result_df["Kelayakan"] = df["credit_worthiness"].map(
            {True: "Layak", False: "Tidak Layak"}
        )

        result_df = self._rename_and_order_columns(result_df)

        with pd.ExcelWriter(export_file, engine="openpyxl") as writer:
            result_df.to_excel(writer, sheet_name="Loan Data", index=False)

        return export_file

    def json_to_excel_with_categories(self, import_file: str, export_file: str) -> str:
        data = self.json_handler.read_json(import_file)
        if data is None:
            raise ValueError(f"Could not read data from {import_file}")

        df = pd.DataFrame(data)
        if df.empty:
            raise ValueError("DataFrame is empty. Please provide valid input data.")

        df = self._convert_numeric_columns(df)
        result_df = pd.DataFrame()

        result_df["Pendapatan"] = df["monthly_income"].apply(
            lambda x: f"{self.convert_currency.toIDR(x)} ({self.loan_categorizer.categorize_income(x)})"
        )

        result_df["Pengeluaran"] = df.apply(
            lambda row: f"{self.convert_currency.toIDR(row['monthly_expenses'])} ({self.loan_categorizer.categorize_expenses(row['monthly_expenses'], row['monthly_income'])})",
            axis=1,
        )

        result_df["Surplus"] = df.apply(
            lambda row: f"{self.convert_currency.toIDR(row['monthly_surplus'])} ({self.loan_categorizer.categorize_surplus(row['monthly_surplus'], row['monthly_income'])})",
            axis=1,
        )

        result_df["Jumlah Pinjaman"] = df.apply(
            lambda row: f"{self.convert_currency.toIDR(row['requested_loan_amount'])} ({self.loan_categorizer.categorize_loan_amount(row['requested_loan_amount'], row['collateral_estimate'])})",
            axis=1,
        )

        result_df["Total Jaminan"] = df["collateral_estimate"].apply(
            lambda x: f"{self.convert_currency.toIDR(x)} ({self.loan_categorizer.categorize_collateral(x)})"
        )

        result_df["Angsuran"] = df.apply(
            lambda row: f"{self.convert_currency.toIDR(row['installment'])} ({self.loan_categorizer.categorize_installment(row['installment'], row['monthly_surplus'])})",
            axis=1,
        )

        result_df["Status Pekerjaan"] = df["employment_status"].map(
            {True: "Tetap", False: "Tidak Tetap"}
        )
        result_df["Riwayat Kredit"] = df["previous_credit_history"].map(
            {True: "Baik", False: "Buruk"}
        )
        result_df["Jangka Waktu"] = df.apply(
            lambda row: f"{row['loan_term']} months ({self.loan_categorizer.categorize_loan_term(row['loan_term'])})",
            axis=1,
        )
        result_df["Kelayakan"] = df["credit_worthiness"].map(
            {True: "Layak", False: "Tidak Layak"}
        )

        result_df = self._rename_and_order_columns(result_df)

        with pd.ExcelWriter(export_file, engine="openpyxl") as writer:
            result_df.to_excel(writer, sheet_name="Loan Data", index=False)

        return export_file
