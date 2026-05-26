import pytest

from route_calculator import (
    calculate_travel_time,
    find_route,
    get_distance,
    get_route_summary,
    parse_route_request,
)


def test_parse_valid_request():
    origin, destination, speed = parse_route_request("Berlin:Munich:120")
    assert origin == "Berlin"
    assert destination == "Munich"
    assert speed == 120


def test_parse_strips_whitespace():
    assert parse_route_request(" Berlin : Munich : 120 ") == (
        "Berlin",
        "Munich",
        120,
    )


def test_parse_accepts_minimum_positive_speed():
    assert parse_route_request("Berlin:Munich:1") == ("Berlin", "Munich", 1)


def test_parse_invalid_format_missing_speed():
    with pytest.raises(ValueError, match="Expected format"):
        parse_route_request("Berlin:Munich")


def test_parse_invalid_format_too_many_fields():
    with pytest.raises(ValueError, match="Expected format"):
        parse_route_request("Berlin:Munich:120:extra")


@pytest.mark.parametrize("speed", ["0", "-1"])
def test_parse_rejects_non_positive_speed(speed):
    with pytest.raises(ValueError, match=f"Speed must be positive, got: {speed}"):
        parse_route_request(f"Berlin:Munich:{speed}")


def test_parse_rejects_non_numeric_speed():
    with pytest.raises(ValueError):
        parse_route_request("Berlin:Munich:fast")


def test_get_distance_direct_connection():
    assert get_distance("Berlin", "Hamburg") == 288


def test_get_distance_another_direct_connection():
    assert get_distance("Frankfurt", "Stuttgart") == 200


def test_get_distance_unknown_origin():
    with pytest.raises(ValueError, match="Unknown location: 'Cologne'"):
        get_distance("Cologne", "Berlin")


def test_get_distance_no_direct_connection():
    with pytest.raises(
        ValueError,
        match="No direct connection from 'Hamburg' to 'Munich'",
    ):
        get_distance("Hamburg", "Munich")


def test_calculate_travel_time_basic():
    assert calculate_travel_time(288, 120) == pytest.approx(2.4)


def test_calculate_travel_time_accepts_speed_one():
    assert calculate_travel_time(7, 1) == pytest.approx(7.0)


@pytest.mark.parametrize("speed", [0, -10])
def test_calculate_travel_time_rejects_non_positive_speed(speed):
    with pytest.raises(ValueError) as exc_info:
        calculate_travel_time(288, speed)

    assert str(exc_info.value) == "Speed must be positive"


def test_find_route_direct_neighbour():
    assert find_route("Berlin", "Hamburg") == ["Berlin", "Hamburg"]


def test_find_route_same_location():
    assert find_route("Berlin", "Berlin") == ["Berlin"]


def test_find_route_multi_hop():
    assert find_route("Hamburg", "Stuttgart") == [
        "Hamburg",
        "Frankfurt",
        "Stuttgart",
    ]


def test_find_route_unknown_location():
    with pytest.raises(ValueError, match="Unknown location"):
        find_route("Berlin", "Cologne")


def test_get_route_summary_contains_cities():
    result = get_route_summary("Berlin:Hamburg:100")
    assert "Berlin" in result
    assert "Hamburg" in result


def test_get_route_summary_contains_distance_and_time():
    result = get_route_summary("Berlin:Hamburg:100")
    assert "Distance: 288 km" in result
    assert "Time: 2.88 h at 100 km/h" in result


def test_get_route_summary_multi_hop():
    result = get_route_summary("Hamburg:Stuttgart:100")
    assert "Route: Hamburg -> Frankfurt -> Stuttgart" in result
    assert "Distance: 690 km" in result
    assert "Time: 6.90 h at 100 km/h" in result


def test_get_route_summary_same_city():
    assert get_route_summary("Berlin:Berlin:50") == (
        "Route: Berlin | Distance: 0 km | Time: 0.00 h at 50 km/h"
    )


def test_get_route_summary_invalid_request():
    with pytest.raises(ValueError, match="Expected format"):
        get_route_summary("Berlin:Hamburg")
