"""File I/O: save/load the inventory engine as JSON or CSV.

Both formats round-trip through the `Product`/`PerishableProduct`
`to_dict`/`from_dict` methods, so persistence stays decoupled from the
in-memory engine logic. Malformed files raise `InvalidDataError`
rather than letting a raw JSONDecodeError/csv error leak out.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import List, Union

from .engine import InventoryEngine
from .exceptions import InvalidDataError
from .models import Product, product_from_dict

CSV_FIELDS = ["type", "sku", "name", "price", "quantity", "category", "expiry_date"]


def save_to_json(engine: InventoryEngine, path: Union[str, Path]) -> None:
    path = Path(path)
    data = [p.to_dict() for p in engine.list_products()]
    with path.open("w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2)


def load_from_json(path: Union[str, Path]) -> InventoryEngine:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"inventory file not found: {path}")
    try:
        with path.open("r", encoding="utf-8") as fh:
            raw = json.load(fh)
    except json.JSONDecodeError as exc:
        raise InvalidDataError(f"invalid JSON in {path}: {exc}") from exc

    if not isinstance(raw, list):
        raise InvalidDataError("top-level JSON must be a list of product objects")

    engine = InventoryEngine()
    products: List[Product] = [product_from_dict(item) for item in raw]
    engine.load_products(products)
    return engine


def save_to_csv(engine: InventoryEngine, path: Union[str, Path]) -> None:
    path = Path(path)
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=CSV_FIELDS)
        writer.writeheader()
        for product in engine.list_products():
            row = product.to_dict()
            writer.writerow({field: row.get(field, "") for field in CSV_FIELDS})


def load_from_csv(path: Union[str, Path]) -> InventoryEngine:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"inventory file not found: {path}")

    engine = InventoryEngine()
    try:
        with path.open("r", encoding="utf-8", newline="") as fh:
            reader = csv.DictReader(fh)
            if reader.fieldnames is None or "sku" not in reader.fieldnames:
                raise InvalidDataError("CSV is missing required headers (e.g. 'sku')")
            products = [
                product_from_dict({k: v for k, v in row.items() if v not in (None, "")})
                for row in reader
            ]
    except csv.Error as exc:
        raise InvalidDataError(f"invalid CSV in {path}: {exc}") from exc

    engine.load_products(products)
    return engine
