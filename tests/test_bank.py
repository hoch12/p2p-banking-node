import unittest
from core.domain import Account

# --- CODE REUSE NOTE ---
# Unit testing logic based on Assignment 11.1 & 11.2 from PV Moodle.
# -----------------------

class TestBankAccount(unittest.TestCase):
    def setUp(self):
        self.acc = Account(10001, 0)

    def test_deposit(self):
        self.acc.deposit(500)
        self.assertEqual(self.acc.balance, 500)

    def test_withdraw(self):
        self.acc.deposit(1000)
        self.acc.withdraw(200)
        self.assertEqual(self.acc.balance, 800)

    def test_insufficient_funds(self):
        self.acc.deposit(100)
        with self.assertRaises(ValueError):
            self.acc.withdraw(500)

if __name__ == '__main__':
    unittest.main()