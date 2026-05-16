from datetime import datetime, timezone
from clinicare_hex_min.core.ports.clock import Clock

class SystemClock(Clock):
    def now(self) -> datetime:
        return datetime.now(timezone.utc)
