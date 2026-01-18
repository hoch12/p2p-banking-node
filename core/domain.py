class Account:
    """
    Represents a bank account within the P2P node.
    """
    def __init__(self, number: int, balance: int = 0):
        self.number = number
        self.balance = balance

    def deposit(self, amount: int):
        if amount < 0:
            raise ValueError("Cannot deposit negative amount")
        self.balance += amount

    def withdraw(self, amount: int):
        if amount < 0:
            raise ValueError("Cannot withdraw negative amount")
        if self.balance < amount:
            raise ValueError("Insufficient funds")
        self.balance -= amount

    def to_dict(self):
        return {"number": self.number, "balance": self.balance}

    @staticmethod
    def from_dict(data):
        return Account(data["number"], data["balance"])