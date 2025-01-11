import json
from dataclasses import dataclass


@dataclass
class JsonHandler:

    def read_json(self, filename: str):
        try:
            with open(filename, "r") as file:
                data = json.load(file)
            return data
        except FileNotFoundError:
            print(f"File {filename} not found.")
            return None
        except json.JSONDecodeError:
            print(f"File {filename} cannot be decoded.")
            return None

    def write_json(self, filename: str, data: dict):
        try:
            with open(filename, "w") as file:
                json.dump(data, file, indent=4)
            print(f"Data successfully written to {filename}")
        except Exception as e:
            print(f"An error occurred while writing to {filename}: {e}")
