"""Class hierarchy modeling products in an inventory system.

`Product` is the base class used for ordinary stock items.
`PerishableProduct` extends it to add an expiry date and overrides
`to_dict`/`from_dict`/`describe` to demonstrate inheritance and
polymorphism (the engine can treat both types uniformly via the
common `Product` interface).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Any, Dict, Optional

from .exceptions import InvalidDataError, InvalidPriceError, InvalidQuantityError

REQUIRED_FIELDS = ("sku", "name", "price", "quantity")


@dataclass
class Product:
    """A basic inventory item."""

    sku: str
    name: str
    price: float
    quantity: int
    category: str = "general"

    def __post_init__(self) -> None:
        if self.price < 0:
            raise InvalidPriceError(f"price cannot be negative: {self.price}")
        if self.quantity < 0:
            raise InvalidQuantityError(f"quantity cannot be negative: {self.quantity}")

    def total_value(self) -> float:
        """Current stock value (price * quantity)."""
        return round(self.price * self.quantity, 2)

    def describe(self) -> str:
        return f"{self.name} (SKU {self.sku}): {self.quantity} units @ {self.price:.2f}"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "product",
            "sku": self.sku,
            "name": self.name,
            "price": self.price,
            "quantity": self.quantity,
            "category": self.category,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Product":
        missing = [f for f in REQUIRED_FIELDS if f not in data]
        if missing:
            raise InvalidDataError(f"missing required field(s): {missing}")
        try:
            return cls(
                sku=str(data["sku"]),
                name=str(data["name"]),
                price=float(data["price"]),
                quantity=int(data["quantity"]),
                category=str(data.get("category", "general")),
            )
        except (TypeError, ValueError) as exc:
            raise InvalidDataError(f"invalid field types in product data: {exc}") from exc


@dataclass
class PerishableProduct(Product):
    """A product that expires and should be tracked/discarded after a date."""

    expiry_date: date = field(default_factory=date.today)

    def is_expired(self, reference_date: Optional[date] = None) -> bool:
        reference_date = reference_date or date.today()
        return reference_date >= self.expiry_date

    def describe(self) -> str:
        base = super().describe()
        status = "EXPIRED" if self.is_expired() else f"expires {self.expiry_date.isoformat()}"
        return f"{base} [{status}]"

    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data["type"] = "perishable"
        data["expiry_date"] = self.expiry_date.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PerishableProduct":
        missing = [f for f in (*REQUIRED_FIELDS, "expiry_date") if f not in data]
        if missing:
            raise InvalidDataError(f"missing required field(s): {missing}")
        try:
            return cls(
                sku=str(data["sku"]),
                name=str(data["name"]),
                price=float(data["price"]),
                quantity=int(data["quantity"]),
                category=str(data.get("category", "general")),
                expiry_date=date.fromisoformat(str(data["expiry_date"])),
            )
        except (TypeError, ValueError) as exc:
            raise InvalidDataError(f"invalid field types in perishable data: {exc}") from exc


def product_from_dict(data: Dict[str, Any]) -> Product:
    """Factory that dispatches to the right Product subclass based on `type`."""
    product_type = data.get("type", "product")
    if product_type == "perishable":
        return PerishableProduct.from_dict(data)
    if product_type == "product":
        return Product.from_dict(data)
    raise InvalidDataError(f"unknown product type: {product_type!r}")
