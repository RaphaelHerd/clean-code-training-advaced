from hypothesis import assume, given
from hypothesis import strategies as st
from hypothesis.strategies import composite, DrawFn
import pytest
from basket import Basket


@composite
def basket_strategy(draw: DrawFn):
    """Generate a Basket containing 0–8 items with realistic names and prices."""
    item_count = draw(st.integers(min_value=0, max_value=8))
    basket = Basket()
    for _ in range(item_count):
        name = draw(st.text(
            alphabet=st.characters(whitelist_categories=("Lu", "Ll")),
            min_size=1,
            max_size=15,
        ))
        price = draw(st.floats(
            min_value=0.0,
            max_value=500.0,
            allow_nan=False,
            allow_infinity=False,
        ))
        basket.add_item(name, round(price, 2))
    return basket

@given(basket_strategy())
def test_total_is_never_negative(basket: Basket):
    assert basket.total() >= 0.0

@given(basket_strategy(), st.floats(min_value=0.01, max_value=500.0, allow_nan=False, allow_infinity=False))
def test_adding_item_increases_total(basket: Basket, price: float):
    price = round(price, 2)
    total_before = basket.total()

    basket.add_item("NewItem", price)

    assert basket.total() > total_before

@given(basket_strategy())
def test_total_equals_sum_of_item_prices(basket: Basket):
    from basket import Item
    expected = sum(
        round(i.price, 2)
        for i in basket._items
    )
    assert basket.total() == pytest.approx(expected)

@given(basket_strategy(), st.text(min_size=1))
def test_removing_unknown_item_does_not_change_basket(basket: Basket, name: str):
    assume(name not in basket.item_names())  # only run when name is truly absent

    total_before = basket.total()
    size_before = len(basket)

    basket.remove_item(name)

    assert basket.total() == pytest.approx(total_before)
    assert len(basket) == size_before

@given(basket_strategy(), st.text(min_size=1, max_size=15), st.floats(min_value=0.01, max_value=500.0, allow_nan=False, allow_infinity=False))
def test_add_then_remove_restores_total(basket: Basket, name: str, price: float):
    assume(name not in basket.item_names())
    price = round(price, 2)
    total_before = basket.total()

    basket.add_item(name, price)
    basket.remove_item(name)

    assert basket.total() == pytest.approx(total_before)