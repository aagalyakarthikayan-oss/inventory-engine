"""The core inventory management engine.

Holds a collection of Product (or subclass) instances keyed by SKU and
exposes CRUD-style operations plus stock in/out helpers that enforce
the domain's invariants (no negative stock, no duplicate SKUs, etc.)
by raising the custom exceptions defined in `exceptions.py`.
"""
from __future__ import annotations

from typing import Dict, Iterable, List

from .exceptions import (
    DuplicateProductError,
    InsufficientStockError,
    InvalidQuantityError,
    ProductNotFoundError,
)
from .models import Product


class InventoryEngine:
    """Manages a collection of products and their stock levels."""

    def __init__(self) -> None:
        self._products: Dict[str, Product] = {}

    # -- CRUD -----------------------------------------------------------
    def add_product(self, product: Product) -> None:
        if product.sku in self._products:
            raise DuplicateProductError(f"product with SKU {product.sku!r} already exists")
        self._products[product.sku] = product

    def get_product(self, sku: str) -> Product:
        try:
            return self._products[sku]
        except KeyError as exc:
            raise ProductNotFoundError(f"no product with SKU {sku!r}") from exc

    def remove_product(self, sku: str) -> Product:
        try:
            return self._products.pop(sku)
        except KeyError as exc:
            raise ProductNotFoundError(f"no product with SKU {sku!r}") from exc

    def list_products(self) -> List[Product]:
        return list(self._products.values())

    def __len__(self) -> int:
        return len(self._products)

    def __contains__(self, sku: str) -> bool:
        return sku in self._products

    # -- Stock movement ---------------------------------------------------
    def restock(self, sku: str, amount: int) -> Product:
        if amount <= 0:
            raise InvalidQuantityError("restock amount must be positive")
        product = self.get_product(sku)
        product.quantity += amount
        return product

    def sell(self, sku: str, amount: int) -> Product:
        if amount <= 0:
            raise InvalidQuantityError("sale amount must be positive")
        product = self.get_product(sku)
        if amount > product.quantity:
            raise InsufficientStockError(
                f"cannot sell {amount} of {sku!r}; only {product.quantity} in stock"
            )
        product.quantity -= amount
        return product

    # -- Queries ----------------------------------------------------------
    def search_by_category(self, category: str) -> List[Product]:
        return [p for p in self._products.values() if p.category == category]

    def search_by_name(self, term: str) -> List[Product]:
        term_lower = term.lower()
        return [p for p in self._products.values() if term_lower in p.name.lower()]

    def total_inventory_value(self) -> float:
        return round(sum(p.total_value() for p in self._products.values()), 2)

    def low_stock(self, threshold: int = 5) -> List[Product]:
        return [p for p in self._products.values() if p.quantity <= threshold]

    # -- Bulk load ----------------------------------------------------------
    def load_products(self, products: Iterable[Product], replace_existing: bool = False) -> None:
        for product in products:
            if replace_existing and product.sku in self._products:
                self._products[product.sku] = product
            else:
                self.add_product(product)
