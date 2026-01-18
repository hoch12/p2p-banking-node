import socket
import threading
from core.bank_service import BankService


class BankNode:
    """
    The Network Layer of the application.

    Implements a multithreaded TCP Server using raw sockets.
    Responsible for accepting connections and delegating tasks to BankService.

    --- CODE REUSE NOTE ---
    The socket handling and threading logic is based on School Assignments 16.1 - 16.3.
    -----------------------

    Attributes:
        ip (str): The IP address to bind to.
        port (int): The TCP port to listen on.
        service (BankService): The business logic controller.
    """

    def __init__(self, ip: str, port: int):
        self.ip = ip
        self.port = port
        self.running = True
        self.service = BankService()

    def start_server(self):
        """
        Initializes the TCP socket, binds to the port, and starts the main listener loop.
        Spawns a new thread for each incoming client connection.
        """
        # Create a raw TCP socket (AF_INET = IPv4, SOCK_STREAM = TCP)
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Allow reusing the address/port immediately after restart
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        try:
            server_socket.bind((self.ip, self.port))
            server_socket.listen(5)  # Backlog of 5 connections
            print(f"[SERVER] Bank Node running on {self.ip}:{self.port}")
            print(f"[SERVER] Ready to accept P2P connections via PuTTY...")

            while self.running:
                # Accept new connection (Blocking call)
                client_socket, client_address = server_socket.accept()

                # --- THREADING (Assignment 16.3) ---
                # Handle each client in a separate thread
                client_thread = threading.Thread(
                    target=self.handle_client,
                    args=(client_socket, client_address)
                )
                client_thread.start()

                # Log active thread count
                print(f"[INFO] Active connections: {threading.active_count() - 1}")

        except Exception as e:
            print(f"[CRITICAL] Server failed: {e}")
        finally:
            server_socket.close()

    def handle_client(self, conn: socket.socket, addr):
        """
        Handles the lifecycle of a single client connection.
        Receives data, decodes it, executes commands via Service, and sends responses.

        Args:
            conn (socket): The connected client socket object.
            addr (tuple): The (IP, Port) of the client.
        """
        print(f"[CONN] {addr[0]} connected.")

        # Set timeout (manual testing friendly)
        conn.settimeout(300)

        try:
            while True:
                # Receive data
                data = conn.recv(1024)
                if not data:
                    break  # Connection closed by client

                # Decode command (UTF-8)
                command_str = data.decode("utf-8").strip()
                if not command_str:
                    continue

                print(f"[RECV] {command_str}")

                # --- PROCESS COMMAND ---
                response = self.service.execute_command(command_str, addr[0])

                # Send response
                conn.sendall(f"{response}\n".encode("utf-8"))

        except socket.timeout:
            print(f"[TIMEOUT] Client {addr[0]} was idle for too long.")
        except ConnectionResetError:
            print(f"[DISCONNECT] Client {addr[0]} forcibly closed connection.")
        except Exception as e:
            print(f"[ERROR] Handling client {addr[0]}: {e}")
        finally:
            conn.close()
            print(f"[CLOSED] Connection with {addr[0]} closed.")