from datetime import date

import pytest

from inventory_engine import persistence
from inventory_engine.engine import InventoryEngine
from inventory_engine.exceptions import InvalidDataError
from inventory_engine.models import PerishableProduct, Product


def make_engine() -> InventoryEngine:
    engine = InventoryEngine()
    engine.add_product(Product(sku="A1", name="Widget", price=2.5, quantity=10, category="tools"))
    engine.add_product(
        PerishableProduct(
            sku="P1", name="Milk", price=1.5, quantity=3, category="dairy", expiry_date=date(2026, 1, 1)
        )
    )
    return engine


def test_json_round_trip(tmp_path):
    engine = make_engine()
    path = tmp_path / "inventory.json"
    persistence.save_to_json(engine, path)

    loaded = persistence.load_from_json(path)
    assert len(loaded) == 2
    assert loaded.get_product("A1").name == "Widget"
    assert isinstance(loaded.get_product("P1"), PerishableProduct)


def test_json_load_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        persistence.load_from_json(tmp_path / "missing.json")


def test_json_load_malformed_json_raises(tmp_path):
    path = tmp_path / "bad.json"
    path.write_text("{not valid json", encoding="utf-8")
    with pytest.raises(InvalidDataError):
        persistence.load_from_json(path)


def test_json_load_wrong_structure_raises(tmp_path):
    path = tmp_path / "bad_structure.json"
    path.write_text('{"not": "a list"}', encoding="utf-8")
    with pytest.raises(InvalidDataError):
        persistence.load_from_json(path)


def test_csv_round_trip(tmp_path):
    engine = make_engine()
    path = tmp_path / "inventory.csv"
    persistence.save_to_csv(engine, path)

    loaded = persistence.load_from_csv(path)
    assert len(loaded) == 2
    assert loaded.get_product("A1").quantity == 10
    assert isinstance(loaded.get_product("P1"), PerishableProduct)


def test_csv_load_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        persistence.load_from_csv(tmp_path / "missing.csv")


def test_csv_load_missing_headers_raises(tmp_path):
    path = tmp_path / "bad.csv"
    path.write_text("not,a,valid,header\n1,2,3,4\n", encoding="utf-8")
    with pytest.raises(InvalidDataError):
        persistence.load_from_csv(path)
