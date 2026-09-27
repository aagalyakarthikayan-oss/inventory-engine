from datetime import date, timedelta

import pytest

from inventory_engine.exceptions import InvalidDataError, InvalidPriceError, InvalidQuantityError
from inventory_engine.models import PerishableProduct, Product, product_from_dict


def test_product_total_value():
    p = Product(sku="A1", name="Widget", price=2.5, quantity=4)
    assert p.total_value() == 10.0


def test_product_negative_price_raises():
    with pytest.raises(InvalidPriceError):
        Product(sku="A1", name="Widget", price=-1, quantity=1)


def test_product_negative_quantity_raises():
    with pytest.raises(InvalidQuantityError):
        Product(sku="A1", name="Widget", price=1, quantity=-1)


def test_product_to_from_dict_round_trip():
    p = Product(sku="A1", name="Widget", price=2.5, quantity=4, category="tools")
    data = p.to_dict()
    rebuilt = Product.from_dict(data)
    assert rebuilt == p


def test_product_from_dict_missing_field_raises():
    with pytest.raises(InvalidDataError):
        Product.from_dict({"sku": "A1", "name": "Widget"})


def test_perishable_is_expired():
    yesterday = date.today() - timedelta(days=1)
    tomorrow = date.today() + timedelta(days=1)
    expired = PerishableProduct(sku="P1", name="Milk", price=1.5, quantity=3, expiry_date=yesterday)
    fresh = PerishableProduct(sku="P2", name="Yogurt", price=1.0, quantity=2, expiry_date=tomorrow)
    assert expired.is_expired() is True
    assert fresh.is_expired() is False


def test_perishable_describe_includes_status():
    yesterday = date.today() - timedelta(days=1)
    expired = PerishableProduct(sku="P1", name="Milk", price=1.5, quantity=3, expiry_date=yesterday)
    assert "EXPIRED" in expired.describe()


def test_perishable_to_from_dict_round_trip():
    p = PerishableProduct(sku="P1", name="Milk", price=1.5, quantity=3, expiry_date=date(2026, 1, 1))
    rebuilt = PerishableProduct.from_dict(p.to_dict())
    assert rebuilt == p


def test_product_from_dict_factory_dispatches_by_type():
    perishable_data = {
        "type": "perishable",
        "sku": "P1",
        "name": "Milk",
        "price": 1.5,
        "quantity": 3,
        "expiry_date": "2026-01-01",
    }
    result = product_from_dict(perishable_data)
    assert isinstance(result, PerishableProduct)

    plain_data = {"type": "product", "sku": "A1", "name": "Widget", "price": 2.5, "quantity": 4}
    result2 = product_from_dict(plain_data)
    assert isinstance(result2, Product)
    assert not isinstance(result2, PerishableProduct)


def test_product_from_dict_factory_unknown_type_raises():
    with pytest.raises(InvalidDataError):
        product_from_dict({"type": "mystery", "sku": "X"})
