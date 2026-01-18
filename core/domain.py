class Account:
    """
    Represents a domain entity for a Bank Account.
    Encapsulates state (balance) and basic business rules (deposit/withdraw logic).

    Attributes:
        number (int): Unique account identifier.
        balance (int): Current funds available in the account.
    """
    def __init__(self, number: int, balance: int = 0):
        self.number = number
        self.balance = balance

    def deposit(self, amount: int):
        """Adds funds to the account. Raises ValueError for negative amounts."""
        if amount < 0:
            raise ValueError("Cannot deposit negative amount")
        self.balance += amount

    def withdraw(self, amount: int):
        """
        Deducts funds from the account.
        Raises ValueError for negative amounts or insufficient funds.
        """
        if amount < 0:
            raise ValueError("Cannot withdraw negative amount")
        if self.balance < amount:
            raise ValueError("Insufficient funds")
        self.balance -= amount

    def to_dict(self):
        """Serializes the account state to a dictionary for JSON storage."""
        return {"number": self.number, "balance": self.balance}

    @staticmethod
    def from_dict(data):
        """Deserializes a dictionary back into an Account object."""
        return Account(data["number"], data["balance"])