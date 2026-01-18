import time
import socket
from shared.persistence.repository import AccountRepository
from shared.structures.LinkedStack import LinkedStack
from shared.structures.LinkedQueue import LinkedQueue


# --- CODE REUSE NOTE ---
# Integrates LinkedStack (History) and LinkedQueue (Buffer) from algorithmic tasks.
# Includes Socket Client logic for P2P communication (Essentials Level).
# -----------------------

class BankService:
    def __init__(self):
        self.repository = AccountRepository()
        self.transaction_history = LinkedStack()
        self.request_queue = LinkedQueue()

        self.my_ips = ["127.0.0.1", "localhost", "0.0.0.0"]

    def _log_transaction(self, message: str):
        timestamp = time.strftime("%H:%M:%S")
        entry = f"[{timestamp}] {message}"
        self.transaction_history.add(entry)
        self.request_queue.add(entry)
        print(f"[LOG] {entry}")

    def _forward_command(self, target_ip: str, command: str) -> str:
        """
        ACTS AS A CLIENT: Connects to another Bank Node to forward a request.
        """
        print(f"[P2P] Forwarding command to {target_ip}: {command}")
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(5)
                s.connect((target_ip, 65525))

                s.sendall(f"{command}\n".encode("utf-8"))

                response = s.recv(1024).decode("utf-8").strip()
                return response
        except ConnectionRefusedError:
            return f"ER Connection refused by {target_ip} (Bank is offline)"
        except socket.timeout:
            return f"ER Timeout connecting to {target_ip}"
        except Exception as e:
            return f"ER P2P Error: {str(e)}"

    def _is_local_account(self, ip_address: str) -> bool:
        """Checks if the account belongs to this node."""
        return ip_address in self.my_ips

    def execute_command(self, command_str: str, client_ip: str) -> str:
        parts = command_str.strip().split()
        if not parts:
            return "ER Empty command"

        cmd = parts[0].upper()

        try:
            # --- BC: Bank Code ---
            if cmd == "BC":
                return f"BC {client_ip}"

            # --- AC: Account Create ---
            elif cmd == "AC":
                import random
                new_num = random.randint(10000, 99999)
                while self.repository.find_by_number(new_num):
                    new_num = random.randint(10000, 99999)
                self.repository.create(new_num)
                self._log_transaction(f"Created account {new_num}")
                return f"AC {new_num}/{client_ip}"

            # --- AD: Account Deposit ---
            elif cmd == "AD":
                if len(parts) != 3: return "ER Invalid format"
                acc_full = parts[1]
                amount = int(parts[2])

                if "/" not in acc_full: return "ER Invalid account format"
                acc_num_str, target_ip = acc_full.split("/")
                acc_num = int(acc_num_str)

                # >>> P2P LOGIC START <<<
                if not self._is_local_account(target_ip):
                    return self._forward_command(target_ip, command_str)
                # >>> P2P LOGIC END <<<

                account = self.repository.find_by_number(acc_num)
                if not account: return "ER Account not found"

                account.deposit(amount)
                self.repository.save_all()
                self._log_transaction(f"Deposit {amount} to {acc_num}")
                return "AD"

            # --- AW: Account Withdrawal ---
            elif cmd == "AW":
                if len(parts) != 3: return "ER Invalid format"
                acc_full = parts[1]
                amount = int(parts[2])

                if "/" not in acc_full: return "ER Invalid account format"
                acc_num_str, target_ip = acc_full.split("/")
                acc_num = int(acc_num_str)

                # >>> P2P LOGIC START <<<
                if not self._is_local_account(target_ip):
                    return self._forward_command(target_ip, command_str)
                # >>> P2P LOGIC END <<<

                account = self.repository.find_by_number(acc_num)
                if not account: return "ER Account not found"

                try:
                    account.withdraw(amount)
                    self.repository.save_all()
                    self._log_transaction(f"Withdraw {amount} from {acc_num}")
                    return "AW"
                except ValueError:
                    return "ER Insufficient funds"

            # --- AB: Account Balance ---
            elif cmd == "AB":
                if len(parts) != 2: return "ER Invalid format"

                acc_full = parts[1]
                if "/" in acc_full:
                    acc_num_str, target_ip = acc_full.split("/")
                    # >>> P2P LOGIC START <<<
                    if not self._is_local_account(target_ip):
                        return self._forward_command(target_ip, command_str)
                    # >>> P2P LOGIC END <<<
                    acc_num = int(acc_num_str)
                else:
                    acc_num = int(acc_full)

                account = self.repository.find_by_number(acc_num)
                if not account: return "ER Account not found"
                return f"AB {account.balance}"

            # --- AR: Account Remove ---
            elif cmd == "AR":
                acc_num = int(parts[1].split("/")[0])
                try:
                    self.repository.delete(acc_num)
                    self._log_transaction(f"Removed account {acc_num}")
                    return "AR"
                except ValueError as e:
                    return f"ER {str(e)}"

            # --- BA: Bank Amount ---
            elif cmd == "BA":
                total = sum(acc.balance for acc in self.repository.get_all_accounts())
                return f"BA {total}"

            # --- BN: Bank Number ---
            elif cmd == "BN":
                count = len(self.repository.get_all_accounts())
                return f"BN {count}"

            else:
                return "ER Unknown command"

        except Exception as e:
            return f"ER System error: {str(e)}"