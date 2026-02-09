from __future__ import annotations

import argparse
from pathlib import Path

from pocwc.api_server import run_api_server


def main() -> None:
    parser = argparse.ArgumentParser(description="Run PoCWC API/UI server")
    parser.add_argument("--db", type=Path, default=Path("data/world.db"))
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8080)
    args = parser.parse_args()
    run_api_server(args.db, args.host, args.port)


if __name__ == "__main__":
    main()
