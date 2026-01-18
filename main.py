import argparse
import sys
from core.server import BankNode


# --- CODE REUSE NOTE ---
# Argument parsing logic is adapted from the 'Image Processing Pipeline' project.
# It ensures consistent CLI usage across my portfolio projects.
# -----------------------

def validate_args():
    """
    Parses and validates command-line arguments.

    Returns:
        argparse.Namespace: An object containing the parsed arguments:
            - port (int): The TCP port to listen on.
            - ip (str): The IP address to bind to.
    """
    parser = argparse.ArgumentParser(description="P2P Banking Node - Distributed System Project")

    # Define arguments with help descriptions
    parser.add_argument(
        "--port",
        type=int,
        default=65525,
        help="The TCP port to listen on (Default: 65525). Range 65525-65535 is recommended."
    )

    parser.add_argument(
        "--ip",
        type=str,
        default="0.0.0.0",
        help="The IP address to bind the server to (Default: 0.0.0.0 for all interfaces)."
    )

    return parser.parse_args()


if __name__ == "__main__":
    """
    Main Application Entry Point.

    1. Parses CLI arguments.
    2. Initializes the BankNode (Network Layer).
    3. Starts the server loop.
    4. Handles graceful shutdown on KeyboardInterrupt (Ctrl+C).
    """
    args = validate_args()

    # Initialize the Bank Node with provided configuration
    node = BankNode(args.ip, args.port)

    try:
        # Start the TCP Server (Blocking call)
        node.start_server()
    except KeyboardInterrupt:
        print("\n[STOP] Server stopped manually by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n[CRITICAL] Unexpected error: {e}")
        sys.exit(1)