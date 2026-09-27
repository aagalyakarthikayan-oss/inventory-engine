# inventory-engine

An object-oriented inventory management engine demonstrating class
hierarchies, custom exceptions, and clean JSON/CSV file I/O — built
for the RabTech Python Software Engineering internship task
("Core Algorithms, OOP Structures & Robust Error Handling").

## Design

- Class hierarchy: Product base class, PerishableProduct subclass
  (inheritance + polymorphism) with expiry tracking.
- Custom exceptions: InvalidPriceError, InvalidQuantityError,
  DuplicateProductError, ProductNotFoundError, InsufficientStockError,
  InvalidDataError.
- Persistence: JSON and CSV save/load via to_dict/from_dict.

## Install

    python3 -m venv .venv
    source .venv/bin/activate
    pip install -e ".[dev]"

## Usage (CLI)

    inventory-engine --file inventory.json add A1 Widget 2.50 10
    inventory-engine --file inventory.json restock A1 5
    inventory-engine --file inventory.json sell A1 3
    inventory-engine --file inventory.json list
    inventory-engine --file inventory.json value

## Running the tests

    pip install -e ".[dev]"
    pytest -v --cov=inventory_engine --cov-report=term-missing
