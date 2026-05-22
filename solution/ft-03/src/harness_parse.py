import atheris
import sys
from route_calculator import parse_route_request


def TestOneInput(data: bytes) -> None:
    text = data.decode("utf-8", errors="replace")

    try:
        parse_route_request(text)

    except ValueError:
        pass


if __name__ == "__main__":
    atheris.Setup(sys.argv, TestOneInput)
    atheris.Fuzz()
