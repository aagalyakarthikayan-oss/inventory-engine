"""Custom exception hierarchy for the inventory engine.

Having a single InventoryError base class lets callers catch all
domain-specific errors with one except clause, while still allowing
fine-grained handling of individual failure modes.
"""
from __future__ import annotations


class InventoryError(Exception):
    """Base class for all inventory-engine domain errors."""


class InvalidQuantityError(InventoryError):
    """Raised when a quantity is negative or otherwise invalid."""


class InvalidPriceError(InventoryError):
    """Raised when a price is negative or otherwise invalid."""


class DuplicateProductError(InventoryError):
    """Raised when adding a product whose SKU already exists."""


class ProductNotFoundError(InventoryError):
    """Raised when looking up, updating, or removing an unknown SKU."""


class InsufficientStockError(InventoryError):
    """Raised when a sale/removal would drive stock below zero."""


class InvalidDataError(InventoryError):
    """Raised when loading malformed/incomplete data from JSON or CSV."""
