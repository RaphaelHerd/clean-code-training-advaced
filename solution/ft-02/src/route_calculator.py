LOCATIONS = {
    "Berlin":    {"Hamburg": 288, "Munich": 585, "Frankfurt": 545},
    "Hamburg":   {"Berlin": 288, "Frankfurt": 490},
    "Munich":    {"Berlin": 585, "Frankfurt": 390, "Stuttgart": 220},
    "Frankfurt": {"Berlin": 545, "Hamburg": 490, "Munich": 390, "Stuttgart": 200},
    "Stuttgart": {"Munich": 220, "Frankfurt": 200},
}


def parse_route_request(request: str):
    """Parse a colon-separated route request: 'ORIGIN:DESTINATION:SPEED_KMH'"""
    parts = request.split(":")
    if len(parts) != 3:
        raise ValueError(f"Expected format 'ORIGIN:DESTINATION:SPEED', got: '{request}'")
    origin      = parts[0].strip()
    destination = parts[1].strip()
    speed       = int(parts[2].strip())
    if speed <= 0:
        raise ValueError(f"Speed must be positive, got: {speed}")
    return origin, destination, speed


def get_distance(origin: str, destination: str) -> int:
    """Return the direct distance (km) between two directly connected locations."""
    if origin not in LOCATIONS:
        raise ValueError(f"Unknown location: '{origin}'")
    if destination not in LOCATIONS[origin]:
        raise ValueError(f"No direct connection from '{origin}' to '{destination}'")
    return LOCATIONS[origin][destination]


def calculate_travel_time(distance: int, speed: int) -> float:
    """Return travel time in hours."""
    if speed <= 0:
        raise ValueError("Speed must be positive")
    return distance / speed


def find_route(origin: str, destination: str) -> list[str]:
    """BFS shortest-hop path. Returns empty list if no route exists."""
    if origin not in LOCATIONS or destination not in LOCATIONS:
        raise ValueError(f"Unknown location: '{origin}' or '{destination}'")
    if origin == destination:
        return [origin]

    visited = set[str]()
    queue   = [(origin, [origin])]

    while queue:
        current, path = queue.pop(0)
        if current == destination:
            return path
        if current in visited:
            continue
        visited.add(current)
        for neighbor in LOCATIONS.get(current, {}):
            if neighbor not in visited:
                queue.append((neighbor, path + [neighbor]))

    return []


def get_route_summary(request: str) -> str:
    """
    Full pipeline: parse request -> find route -> compute distance & time.
    Input format: 'ORIGIN:DESTINATION:SPEED_KMH'
    """
    origin, destination, speed = parse_route_request(request)
    route = find_route(origin, destination)

    if not route:
        raise ValueError(f"No route found from '{origin}' to '{destination}'")

    total_distance = 0
    for i in range(len(route) - 1):
        total_distance += get_distance(route[i], route[i + 1])

    travel_time = calculate_travel_time(total_distance, speed)
    return (
        f"Route: {' -> '.join(route)} | "
        f"Distance: {total_distance} km | "
        f"Time: {travel_time:.2f} h at {speed} km/h"
    )
