import argparse
import sys
from core.server import BankNode


# --- CODE REUSE NOTE ---
# Argument parsing adapted from 'Image Processing Pipeline'.
# -----------------------

def validate_args():
    parser = argparse.ArgumentParser(description="P2P Banking Node")
    parser.add_argument("--port", type=int, default=65525, help="Port (65525-65535)")
    parser.add_argument("--ip", type=str, default="0.0.0.0", help="Bind IP")
    return parser.parse_args()


if __name__ == "__main__":
    args = validate_args()

    node = BankNode(args.ip, args.port)
    try:
        node.start_server()
    except KeyboardInterrupt:
        sys.exit(0)