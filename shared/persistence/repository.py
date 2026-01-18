import json
from pathlib import Path
from typing import Dict
from core.domain import Account

# --- CODE REUSE NOTE ---
# The logic for file handling is adapted from 'Image Processing Pipeline' (exporter.py).
# Implements Repository Pattern for separation of concerns.
# -----------------------

class AccountRepository:
    def __init__(self, data_file: str = "data/accounts.json"):
        self.data_file = Path(data_file)
        self.data_file.parent.mkdir(parents=True, exist_ok=True)
        self._accounts: Dict[int, Account] = {}
        self._load()

    def _load(self):
        if not self.data_file.exists():
            return
        try:
            with open(self.data_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                for acc_data in data:
                    account = Account.from_dict(acc_data)
                    self._accounts[account.number] = account
            print(f"[INFO] Loaded {len(self._accounts)} accounts.")
        except Exception as e:
            print(f"[ERROR] Failed to load database: {e}")

    def save_all(self):
        data = [acc.to_dict() for acc in self._accounts.values()]
        try:
            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"[CRITICAL] Failed to save database: {e}")

    def create(self, number: int) -> Account:
        if number in self._accounts:
            raise ValueError("Account already exists")
        new_account = Account(number)
        self._accounts[number] = new_account
        self.save_all()
        return new_account

    def find_by_number(self, number: int) -> Account:
        return self._accounts.get(number)

    def delete(self, number: int):
        if number not in self._accounts:
            raise ValueError("Account not found")
        if self._accounts[number].balance > 0:
            raise ValueError("Cannot delete account with funds")
        del self._accounts[number]
        self.save_all()

    def get_all_accounts(self) -> list[Account]:
        return list(self._accounts.values())