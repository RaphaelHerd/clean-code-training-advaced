import atheris
import base64
import sys
import traceback
from route_calculator import get_route_summary


SEEN_FAILURES = set()
FINDINGS_LOG = "fuzz_findings.log"


def record_failure(data: bytes, text: str, exc: Exception) -> None:
    """Record each distinct application crash once, then let fuzzing continue."""
    traceback_entry = traceback.extract_tb(exc.__traceback__)[-1]
    failure_key = (
        type(exc).__name__,
        traceback_entry.filename,
        traceback_entry.lineno,
    )

    if failure_key in SEEN_FAILURES:
        return

    SEEN_FAILURES.add(failure_key)
    finding = (
        "\n"
        f"Exception type : {type(exc).__name__}\n"
        f"Location       : {traceback_entry.filename}:{traceback_entry.lineno}\n"
        f"Input repr     : {text!r}\n"
        f"Input base64   : {base64.b64encode(data).decode('ascii')}\n"
    )

    print(finding, flush=True)
    with open(FINDINGS_LOG, "a", encoding="utf-8") as log_file:
        log_file.write(finding)


def TestOneInput(data: bytes) -> None:
    """
    Atheris calls this function repeatedly with random/mutated byte sequences.
    Our job: convert those bytes into a string and feed it to the application.
    """
    # Decode the raw fuzz bytes into a Python string.
    # errors="replace" swaps invalid UTF-8 for U+FFFD instead of raising.
    text = data.decode("utf-8", errors="replace")

    try:
        get_route_summary(text)

    except ValueError:
        # Expected application behaviour: unknown city, wrong numeric format,
        # etc. Suppress it so fuzzing can continue.
        pass

    except Exception as exc:
        # Collection mode: record unexpected application failures and keep
        # fuzzing so later bug categories can be reached in the same run.
        record_failure(data, text, exc)


if __name__ == "__main__":
    atheris.Setup(sys.argv, TestOneInput)
    atheris.Fuzz()


# CRASH #1
# Input that caused it : b"" / ""
# Exception type       : IndexError
# Root cause (line)    : route_calculator.py:14 assumes parts[1] exists.
# Fix idea             : Validate that the request has exactly 3 fields before
#                        reading origin, destination, and speed.

# CRASH #2
# Input that caused it : b"Berlin:Munich" / "Berlin:Munich"
# Exception type       : IndexError
# Root cause (line)    : route_calculator.py:15 assumes parts[2] exists.
# Fix idea             : Reject missing speed with a controlled ValueError.

# CRASH #3
# Input that caused it : b"Berlin:Munich:0" / "Berlin:Munich:0"
# Exception type       : ZeroDivisionError
# Root cause (line)    : route_calculator.py:26 divides by speed without
#                        checking whether speed is zero.
# Fix idea             : Validate speed > 0 before calculating travel time.


# REFLECTION
#
# 1. What kinds of bugs did the fuzzer find that a typical unit test would
#    likely miss?
#    It found malformed input shapes and boundary values: empty input, missing
#    fields, and zero speed. These are easy to omit when unit tests focus only
#    on normal route requests.
#
# 2. How does Atheris use coverage feedback to guide input mutation?
#    Atheris keeps inputs that reach new code paths or branches, then mutates
#    them further. With a corpus, valid route-like strings help it reach parsing,
#    route lookup, and travel-time calculation faster.
#
# 3. When would you prefer fuzzing over property-based testing?
#    Prefer fuzzing when the input space is large, byte-oriented, parser-like,
#    or when you mainly want to discover crashes you did not predict. Prefer
#    property-based tests when you can state expected invariants clearly.
#
# 4. What are the limitations of this fuzzing approach for this application?
#    It mostly detects uncaught exceptions. It does not know whether a route or
#    travel time is semantically correct unless the harness adds assertions or
#    oracles for those properties.
