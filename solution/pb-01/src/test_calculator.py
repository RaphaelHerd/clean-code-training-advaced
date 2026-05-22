from hypothesis import Verbosity, given, settings
from hypothesis import strategies as st
from calculator import add


@given(st.integers(), st.integers())
def test_add_commutativity(a: int, b: int):
    # Changing the order of arguments should not change the result
    assert add(a, b) == add(b, a)

@given(st.integers(), st.integers(), st.integers())
def test_associativity(a: int, b: int, c: int):
    assert add(add(a, b), c) == add(a, add(b, c))
    
@given(st.integers())
def test_identity(a: int):
    assert add(a, 0) == a
    assert add(0, a) == a

@given(st.integers())
def test_add_additive_property(a: int):
    assert add(add(a, 1), 1) == add(a, 2)
    
@settings(max_examples=10, verbosity=Verbosity.verbose)
@given(st.integers(min_value=-100, max_value=100), st.integers(min_value=-100, max_value=100))
def test_add_commutativity_verbose(a: int, b: int):
    assert add(a, b) == add(b, a)