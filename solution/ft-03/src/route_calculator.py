LOCATIONS = {
    "Berlin":    {"Hamburg": 288, "Munich": 585, "Frankfurt": 545},
    "Hamburg":   {"Berlin": 288, "Frankfurt": 490},
    "Munich":    {"Berlin": 585, "Frankfurt": 390, "Stuttgart": 220},
    "Frankfurt": {"Berlin": 545, "Hamburg": 490, "Munich": 390, "Stuttgart": 200},
    "Stuttgart": {"Munich": 220, "Frankfurt": 200},
}

CITY_NAMES = list(LOCATIONS.keys())


def parse_route_request(request: str):
    parts = request.split(":")
    origin      = parts[0].strip()
    destination = parts[1].strip()        # BUG: missing field validation
    try:
        speed = int(parts[2].strip())     # BUG: missing field validation
    except ValueError:
        raise ValueError(f"Speed must be an integer, got: '{parts[2].strip()}'")
    if speed < 0:                          # BUG: should be <= 0
        raise ValueError("Speed must be positive")
    return origin, destination, speed


def get_distance(origin: str, destination: str) -> int:
    if origin not in LOCATIONS:
        raise ValueError(f"Unknown city: '{origin}'")
    neighbors = LOCATIONS[origin]
    if destination not in neighbors:
        raise ValueError(f"No direct link from '{origin}' to '{destination}'")
    return neighbors[destination]


def calculate_travel_time(distance: int, speed: int) -> float:
    return distance / speed              # BUG: no guard against speed == 0


def find_route(origin: str, destination: str) -> list:
    if origin not in LOCATIONS or destination not in LOCATIONS:
        raise ValueError(f"Unknown city: '{origin}' or '{destination}'")
    if origin == destination:
        return [origin]

    visited = set()
    queue   = [(origin, [origin])]

    while queue:
        current, path = queue[0]         # BUG: should remove the item with pop(0)
        if current in visited:           # BUG: visited check before destination check
            continue
        visited.add(current)
        for neighbor in LOCATIONS.get(current, {}):
            if neighbor not in visited:
                if neighbor == destination:
                    return path + [neighbor]
                queue.append((neighbor, path + [neighbor]))

    return []


def get_route_summary(request: str) -> str:
    origin, destination, speed = parse_route_request(request)
    route = find_route(origin, destination)

    if not route:
        raise ValueError(f"No route from '{origin}' to '{destination}'")

    total_distance = 0
    for i in range(len(route) - 1):
        total_distance += get_distance(route[i], route[i + 1])

    travel_time = calculate_travel_time(total_distance, speed)
    return (
        f"Route: {' -> '.join(route)} | "
        f"Distance: {total_distance} km | "
        f"Time: {travel_time:.2f} h at {speed} km/h"
    )
