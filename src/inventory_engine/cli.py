"""A small command-line front-end for the inventory engine.

Supports loading/saving a JSON inventory file and performing a single
operation per invocation (add, restock, sell, list, value). Kept
intentionally simple; the engine and models are fully usable as a
library without this CLI.
"""
from __future__ import annotations

import argparse
import sys
from typing import List, Optional

from . import persistence
from .engine import InventoryEngine
from .exceptions import InventoryError
from .models import Product

EXIT_OK = 0
EXIT_NOT_FOUND = 1
EXIT_INVALID_INPUT = 2
EXIT_UNEXPECTED_ERROR = 3


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="inventory-engine", description="OOP inventory engine CLI.")
    parser.add_argument("--file", "-f", required=True, help="Path to the JSON inventory file.")

    sub = parser.add_subparsers(dest="command", required=True)

    add_p = sub.add_parser("add", help="Add a new product.")
    add_p.add_argument("sku")
    add_p.add_argument("name")
    add_p.add_argument("price", type=float)
    add_p.add_argument("quantity", type=int)
    add_p.add_argument("--category", default="general")

    restock_p = sub.add_parser("restock", help="Add stock to an existing product.")
    restock_p.add_argument("sku")
    restock_p.add_argument("amount", type=int)

    sell_p = sub.add_parser("sell", help="Remove stock from an existing product.")
    sell_p.add_argument("sku")
    sell_p.add_argument("amount", type=int)

    sub.add_parser("list", help="List all products.")
    sub.add_parser("value", help="Print total inventory value.")

    return parser


def _load_or_new(path: str) -> InventoryEngine:
    try:
        return persistence.load_from_json(path)
    except FileNotFoundError:
        return InventoryEngine()


def run(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        engine = _load_or_new(args.file)

        if args.command == "add":
            engine.add_product(
                Product(sku=args.sku, name=args.name, price=args.price, quantity=args.quantity, category=args.category)
            )
            persistence.save_to_json(engine, args.file)
            print(f"added {args.sku}")

        elif args.command == "restock":
            product = engine.restock(args.sku, args.amount)
            persistence.save_to_json(engine, args.file)
            print(product.describe())

        elif args.command == "sell":
            product = engine.sell(args.sku, args.amount)
            persistence.save_to_json(engine, args.file)
            print(product.describe())

        elif args.command == "list":
            for product in engine.list_products():
                print(product.describe())

        elif args.command == "value":
            print(f"{engine.total_inventory_value():.2f}")

    except InventoryError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return EXIT_INVALID_INPUT
    except Exception as exc:
        print(f"unexpected error: {exc}", file=sys.stderr)
        return EXIT_UNEXPECTED_ERROR

    return EXIT_OK


def main() -> None:
    sys.exit(run())


if __name__ == "__main__":
    main()
