import atheris
import sys
from route_calculator import find_route, CITY_NAMES


def TestOneInput(data: bytes) -> None:
    if len(data) < 2:
        return

    fdp = atheris.FuzzedDataProvider(data)
    origin      = fdp.PickValueInList(CITY_NAMES)
    destination = fdp.PickValueInList(CITY_NAMES)

    try:
        find_route(origin, destination)

    except ValueError:
        pass


if __name__ == "__main__":
    atheris.Setup(sys.argv, TestOneInput)
    atheris.Fuzz()
