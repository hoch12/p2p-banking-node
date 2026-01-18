import time
from shared.persistence.repository import AccountRepository
from shared.structures.LinkedStack import LinkedStack
from shared.structures.LinkedQueue import LinkedQueue


# --- CODE REUSE NOTE ---
# Integrates LinkedStack (History) and LinkedQueue (Buffer) from algorithmic tasks.
# -----------------------

class BankService:
    def __init__(self):
        self.repository = AccountRepository()
        self.transaction_history = LinkedStack()
        self.request_queue = LinkedQueue()

    def _log_transaction(self, message: str):
        timestamp = time.strftime("%H:%M:%S")
        entry = f"[{timestamp}] {message}"
        self.transaction_history.add(entry)
        self.request_queue.add(entry)
        print(f"[LOG] {entry}")

    def execute_command(self, command_str: str, client_ip: str) -> str:
        parts = command_str.strip().split()
        if not parts:
            return "ER Empty command"

        cmd = parts[0].upper()

        try:
            if cmd == "BC":
                return f"BC {client_ip}"

            elif cmd == "AC":
                import random
                new_num = random.randint(10000, 99999)
                while self.repository.find_by_number(new_num):
                    new_num = random.randint(10000, 99999)
                self.repository.create(new_num)
                self._log_transaction(f"Created account {new_num}")
                return f"AC {new_num}/{client_ip}"

            elif cmd == "AD":
                if len(parts) != 3: return "ER Invalid format"
                acc_full = parts[1]
                amount = int(parts[2])

                if "/" not in acc_full: return "ER Invalid account format"
                acc_num = int(acc_full.split("/")[0])

                account = self.repository.find_by_number(acc_num)
                if not account: return "ER Account not found"

                account.deposit(amount)
                self.repository.save_all()
                self._log_transaction(f"Deposit {amount} to {acc_num}")
                return "AD"

            elif cmd == "AW":
                if len(parts) != 3: return "ER Invalid format"
                acc_full = parts[1]
                amount = int(parts[2])
                acc_num = int(acc_full.split("/")[0])

                account = self.repository.find_by_number(acc_num)
                if not account: return "ER Account not found"

                try:
                    account.withdraw(amount)
                    self.repository.save_all()
                    self._log_transaction(f"Withdraw {amount} from {acc_num}")
                    return "AW"
                except ValueError:
                    return "ER Insufficient funds"

            elif cmd == "AB":
                if len(parts) != 2: return "ER Invalid format"
                acc_num = int(parts[1].split("/")[0])
                account = self.repository.find_by_number(acc_num)
                if not account: return "ER Account not found"
                return f"AB {account.balance}"

            elif cmd == "AR":
                acc_num = int(parts[1].split("/")[0])
                try:
                    self.repository.delete(acc_num)
                    self._log_transaction(f"Removed account {acc_num}")
                    return "AR"
                except ValueError as e:
                    return f"ER {str(e)}"

            elif cmd == "BA":
                total = sum(acc.balance for acc in self.repository.get_all_accounts())
                return f"BA {total}"

            elif cmd == "BN":
                count = len(self.repository.get_all_accounts())
                return f"BN {count}"

            else:
                return "ER Unknown command"

        except Exception as e:
            return f"ER System error: {str(e)}"