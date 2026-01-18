import socket
import threading
from core.bank_service import BankService


# --- CODE REUSE NOTE ---
# TCP Server logic based on School Assignment 16.1 & 16.3 (Threading).
# -----------------------

class BankNode:
    def __init__(self, ip: str, port: int):
        self.ip = ip
        self.port = port
        self.running = True
        self.service = BankService()

    def start_server(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        try:
            server_socket.bind((self.ip, self.port))
            server_socket.listen(5)
            print(f"[SERVER] Bank Node running on {self.ip}:{self.port}")

            while self.running:
                client_socket, client_addr = server_socket.accept()
                client_thread = threading.Thread(
                    target=self.handle_client,
                    args=(client_socket, client_addr)
                )
                client_thread.start()

        except Exception as e:
            print(f"[CRITICAL] Server failed: {e}")
        finally:
            server_socket.close()

    def handle_client(self, conn: socket.socket, addr):
        print(f"[CONN] {addr[0]} connected.")
        conn.settimeout(300)

        try:
            while True:
                data = conn.recv(1024)
                if not data: break

                cmd = data.decode("utf-8").strip()
                if not cmd: continue

                print(f"[RECV] {cmd}")
                response = self.service.execute_command(cmd, addr[0])
                conn.sendall(f"{response}\n".encode("utf-8"))

        except Exception:
            pass
        finally:
            conn.close()