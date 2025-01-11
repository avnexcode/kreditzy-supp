from module.loan_data import LoanData
from module.loan_converter import LoanConverter
from module.loan_probability import LoanProbability
from module.loan_id3 import LoanID3
from datetime import datetime
import os


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def print_menu():
    print("\n=== Loan Data Processing System ===")
    print("1. Generate New Loan Data")
    print("2. Update Existing Loan Data")
    print("3. Convert JSON to Excel (Basic)")
    print("4. Convert JSON to Excel (With Categories)")
    print("5. Convert JSON to SQL")
    print("6. Generate Probabilities")
    print("7. Calculate Entrophy Gain")
    print("8. Generate & Process Complete Flow")
    print("0. Exit")
    print("=" * 35)


def get_timestamp():
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def process_complete_flow():
    timestamp = get_timestamp()
    loan_data = LoanData()
    converter = LoanConverter()
    probability = LoanProbability()

    print("\nProcessing complete flow...")

    generated_file = loan_data.generate(f"./data/json/generated_{timestamp}.json")
    print(f"Generated data saved to: {generated_file}")

    updated_file = loan_data.update(
        f"./data/json/generated_{timestamp}.json",
        f"./data/json/updated_{timestamp}.json",
    )
    print(f"Updated data saved to: {updated_file}")

    excel_file = converter.json_to_excel(
        f"./data/json/updated_{timestamp}.json",
        f"./data/json/loan_data_{timestamp}.xlsx",
    )
    print(f"Basic Excel file generated: {excel_file}")

    excel_categories_file = converter.json_to_excel_with_categories(
        f"./data/json/updated_{timestamp}.json",
        f"./data/json/loan_data_categories_{timestamp}.xlsx",
    )
    print(f"Categorized Excel file generated: {excel_categories_file}")

    generated_probabilities = probability.calculate("./data/json/final.json")
    print(f"Probabilities file generated: {generated_probabilities}")


def main():
    loan_data = LoanData()
    converter = LoanConverter()
    probability = LoanProbability()
    loan_id3 = LoanID3()

    while True:
        clear_screen()
        print_menu()

        try:
            choice = input("Enter your choice (0-5): ")

            if choice == "0":
                print("\nThank you for using the system. Goodbye!")
                break

            timestamp = get_timestamp()

            if choice == "1":
                generated_file = loan_data.generate(
                    f"./data/json/generated_{timestamp}.json"
                )
                print(f"\nGenerated data saved to: {generated_file}")

            elif choice == "2":
                input_file = input("\nEnter input JSON file path: ")
                output_file = f"./data/json/updated_{timestamp}.json"
                updated_file = loan_data.update(input_file, output_file)
                print(f"Updated data saved to: {updated_file}")

            elif choice == "3":
                input_file = input("\nEnter input JSON file path: ")
                output_file = f"./data/json/loan_data_{timestamp}.xlsx"
                excel_file = converter.json_to_excel(input_file, output_file)
                print(f"Excel file generated: {excel_file}")

            elif choice == "4":
                input_file = input("\nEnter input JSON file path: ")
                output_file = f"./data/json/loan_data_categories_{timestamp}.xlsx"
                excel_file = converter.json_to_excel_with_categories(
                    input_file, output_file
                )
                print(f"Excel file with categories generated: {excel_file}")

            elif choice == "5":
                input_file = input("\nEnter input JSON file path: ")
                output_file = f"./data/sql/loan_data_sql_{timestamp}.sql"
                excel_file = converter.json_to_sql(input_file, output_file)
                print(f"Excel file with categories generated: {excel_file}")

            elif choice == "6":
                input_file = input("\nEnter input JSON file path: ")
                generated_probabilities = probability.calculate(input_file)
                probability.print_analysis_results(generated_probabilities)

            elif choice == "7":
                input_file = input("\nEnter input JSON file path: ")
                results = loan_id3.analyze_credit_entropy(input_file)
                loan_id3.print_entropy_analysis(results)

            elif choice == "8":
                process_complete_flow()

            else:
                print("\nInvalid choice! Please enter a number between 0 and 5.")

            input("\nPress Enter to continue...")

        except Exception as e:
            print(f"\nError: {str(e)}")
            input("\nPress Enter to continue...")


if __name__ == "__main__":
    main()
