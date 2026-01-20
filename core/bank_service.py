import time
import socket
from shared.persistence.repository import AccountRepository
from shared.structures.LinkedStack import LinkedStack
from shared.structures.LinkedQueue import LinkedQueue


class BankService:
    """
    The Business Logic Layer of the P2P Banking Node.

    This class acts as a controller that:
    1. Validates and executes incoming commands.
    2. Manages data persistence via AccountRepository.
    3. Handles P2P routing (forwarding commands to other nodes).
    4. Logs activity using custom Linked structures.

    Attributes:
        repository (AccountRepository): Access to data storage.
        transaction_history (LinkedStack): LIFO log of operations.
        request_queue (LinkedQueue): FIFO buffer for incoming requests.
        my_ips (list): List of IP addresses identified as 'local'.
    """

    def __init__(self):
        self.repository = AccountRepository()

        # --- CODE REUSE NOTE ---
        # Integrates LinkedStack (History) and LinkedQueue (Buffer) from algorithmic tasks.
        # -----------------------
        self.transaction_history = LinkedStack()
        self.request_queue = LinkedQueue()

        # --- FIX: Dynamic IP Detection ---
        # We start with standard loopback addresses
        self.my_ips = ["127.0.0.1", "localhost", "0.0.0.0"]

        # Now we try to find the REAL LAN IP address of this computer (e.g., 10.2.7.132)
        # This prevents the "Self-Forwarding Loop" error.
        try:
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            if local_ip not in self.my_ips:
                self.my_ips.append(local_ip)

            # Print for debugging so you can see what IPs are considered local
            print(f"[INFO] BankService initialized. My local IPs: {self.my_ips}")
        except Exception as e:
            print(f"[WARN] Could not detect local IP: {e}")

    def _log_transaction(self, message: str):
        """
        Logs an event to both the Audit Log (Stack) and Processing Buffer (Queue).
        Demonstrates the usage of custom data structures.

        Args:
            message (str): The transaction details to log.
        """
        timestamp = time.strftime("%H:%M:%S")
        entry = f"[{timestamp}] {message}"
        self.transaction_history.add(entry)
        self.request_queue.add(entry)
        print(f"[LOG] {entry}")

    def _forward_command(self, target_ip: str, command: str) -> str:
        """
        Acts as a TCP CLIENT to forward a command to a remote Bank Node.
        Used when the target account IP does not match the local node.

        Args:
            target_ip (str): The IP address of the remote bank.
            command (str): The raw command string to forward.

        Returns:
            str: The response from the remote server or an error message.
        """
        print(f"[P2P] Forwarding command to {target_ip}: {command}")
        try:
            # We assume all nodes listen on port 65525 as per assignment
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(5)  # Avoid hanging indefinitely
                s.connect((target_ip, 65525))
                s.sendall(f"{command}\n".encode("utf-8"))

                # Wait for response
                response = s.recv(1024).decode("utf-8").strip()
                return response
        except ConnectionRefusedError:
            return f"ER Connection refused by {target_ip} (Bank is offline)"
        except socket.timeout:
            return f"ER Timeout connecting to {target_ip}"
        except Exception as e:
            return f"ER P2P Error: {str(e)}"

    def _is_local_account(self, ip_address: str) -> bool:
        """Determines if the request is for this node or a remote peer."""
        return ip_address in self.my_ips

    def execute_command(self, command_str: str, client_ip: str) -> str:
        """
        Parses and executes the banking protocol commands.

        Supported Commands:
        - BC: Bank Check
        - AC: Account Create
        - AD: Account Deposit (Supports P2P forwarding)
        - AW: Account Withdraw (Supports P2P forwarding)
        - AB: Account Balance (Supports P2P forwarding)
        - AR: Account Remove
        - BA: Bank Amount (Total)
        - BN: Bank Number (Count)

        Args:
            command_str (str): The raw command string received from client.
            client_ip (str): The IP address of the client (for logging/BC).

        Returns:
            str: The protocol response string.
        """
        parts = command_str.strip().split()
        if not parts:
            return "ER Empty command"

        cmd = parts[0].upper()

        try:
            # --- BC: Bank Check ---
            if cmd == "BC":
                return f"BC {client_ip}"

            # --- AC: Account Create ---
            elif cmd == "AC":
                import random
                new_num = random.randint(10000, 99999)
                # Ensure uniqueness
                while self.repository.find_by_number(new_num):
                    new_num = random.randint(10000, 99999)

                self.repository.create(new_num)
                self._log_transaction(f"Created account {new_num}")
                return f"AC {new_num}/{client_ip}"

            # --- AD: Deposit ---
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

            # --- AW: Withdraw ---
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

            # --- AB: Balance ---
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

            # --- AR: Remove ---
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