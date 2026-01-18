import json
from pathlib import Path
from typing import Dict
from core.domain import Account

class AccountRepository:
    """
    Handles data persistence for Bank Accounts using the Repository Pattern.
    Separates the data access layer (JSON file I/O) from the business logic.

    --- CODE REUSE NOTE ---
    The file handling logic (Path management, read/write cycles) is adapted
    from my previous 'Image Processing Pipeline' project (specifically CSVExporter).
    -----------------------

    Attributes:
        data_file (Path): The file path where accounts are stored (JSON).
        _accounts (Dict[int, Account]): In-memory cache of loaded accounts.
    """
    def __init__(self, data_file: str = "data/accounts.json"):
        self.data_file = Path(data_file)
        # Ensure the directory exists
        self.data_file.parent.mkdir(parents=True, exist_ok=True)
        self._accounts: Dict[int, Account] = {}
        self._load()

    def _load(self):
        """Internal method to load data from the JSON file into memory on startup."""
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
        """Persists the current state of all accounts to the JSON file."""
        data = [acc.to_dict() for acc in self._accounts.values()]
        try:
            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"[CRITICAL] Failed to save database: {e}")

    def create(self, number: int) -> Account:
        """Creates and saves a new account. Raises ValueError if it already exists."""
        if number in self._accounts:
            raise ValueError("Account already exists")
        new_account = Account(number)
        self._accounts[number] = new_account
        self.save_all()
        return new_account

    def find_by_number(self, number: int) -> Account:
        """Retrieves an account by its ID. Returns None if not found."""
        return self._accounts.get(number)

    def delete(self, number: int):
        """Deletes an account. Raises ValueError if account has funds or doesn't exist."""
        if number not in self._accounts:
            raise ValueError("Account not found")
        if self._accounts[number].balance > 0:
            raise ValueError("Cannot delete account with funds")
        del self._accounts[number]
        self.save_all()

    def get_all_accounts(self) -> list[Account]:
        """Returns a list of all registered accounts."""
        return list(self._accounts.values())