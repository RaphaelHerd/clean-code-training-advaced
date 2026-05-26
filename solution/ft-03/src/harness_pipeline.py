import atheris
import sys
from route_calculator import get_route_summary, CITY_NAMES


# RAW VS. STRUCTURED
#
# Raw fuzzing mutates arbitrary bytes and hopes they become a useful request
# such as "Berlin:Munich:120".
#
# This structured harness maps bytes into:
# - a valid origin city
# - a valid destination city
# - an integer speed
#
# That means most generated inputs reach the full route pipeline instead of
# being rejected early by parsing or unknown-city validation.
#
# CRASHES
#
# CRASH #1
# Harness that found it : harness_parse.py
# Example input         : "" or "Berlin"
# Exception type        : IndexError
# Root cause            : parse_route_request indexes parts[1] / parts[2]
#                         before validating the number of fields.
# Fix                   : check len(parts) == 3 before indexing.
#
# CRASH #2
# Harness that found it : harness_find_route.py
# Example input         : any non-identical valid city pair, e.g.
#                         Berlin -> Stuttgart
# Failure type          : libFuzzer timeout
# Root cause            : find_route uses queue[0], so it reads the first
#                         queue item without removing it.
# Fix                   : use queue.pop(0) to consume the next queue item.
#
# CRASH #3
# Harness that found it : harness_pipeline.py
# Example request       : "Berlin:Berlin:0"
# Exception type        : ZeroDivisionError
# Root cause            : parse_route_request accepts speed 0, and
#                         calculate_travel_time divides by speed.
# Fix                   : reject speed <= 0 before calculating travel time.
#
# REFLECTION
#
# 1. Lower-level harnesses find focused bugs faster because they skip unrelated
#    setup and validation.
# 2. The dictionary gives libFuzzer useful tokens such as city names, ":", "0",
#    and "-1". Without it, these strings must be discovered byte by byte.
# 3. PickValueInList prevents this harness from testing unknown-city handling.
#    That is acceptable here because the goal is to reach deeper route logic.
# 4. Combine raw-byte and structured fuzzing when both input syntax and deeper
#    business logic need coverage.


def TestOneInput(data: bytes) -> None:
    if len(data) < 4:
        return

    fdp = atheris.FuzzedDataProvider(data)
    origin      = fdp.PickValueInList(CITY_NAMES)
    destination = fdp.PickValueInList(CITY_NAMES)
    speed       = fdp.ConsumeInt(4)

    request = f"{origin}:{destination}:{speed}"

    try:
        get_route_summary(request)

    except ValueError:
        pass


if __name__ == "__main__":
    atheris.Setup(sys.argv, TestOneInput)
    atheris.Fuzz()
