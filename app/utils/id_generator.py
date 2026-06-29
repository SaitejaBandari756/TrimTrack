"""
Snowflake ID Generator
━━━━━━━━━━━━━━━━━━━━━━
Generates 63-bit unique IDs for distributed systems.

Structure (63 bits total):
┌──────────────────┬────────────┬──────────────┐
│ 41-bit timestamp │ 10-bit     │ 12-bit       │
│ (ms since epoch) │ machine ID │ sequence num │
└──────────────────┴────────────┴──────────────┘

- Supports up to 1024 machines (0–1023)
- Up to 4096 IDs per millisecond per machine
- ~69 years of unique timestamps from custom epoch
"""

import time
import threading
import uuid

# Custom epoch: 2024-01-01 00:00:00 UTC (in milliseconds)
CUSTOM_EPOCH = 1704067200000

# Bit allocation
TIMESTAMP_BITS = 41
MACHINE_ID_BITS = 10
SEQUENCE_BITS = 12

# Max values
MAX_MACHINE_ID = (1 << MACHINE_ID_BITS) - 1  # 1023
MAX_SEQUENCE = (1 << SEQUENCE_BITS) - 1  # 4095

# Bit shifts
MACHINE_ID_SHIFT = SEQUENCE_BITS
TIMESTAMP_SHIFT = SEQUENCE_BITS + MACHINE_ID_BITS


class SnowflakeIDGenerator:
    """
    Thread-safe Snowflake ID generator.

    Each instance is bound to a machine_id (0–1023).
    Generates monotonically increasing, globally unique 63-bit IDs.
    """

    def __init__(self, machine_id: int = 0):
        if not 0 <= machine_id <= MAX_MACHINE_ID:
            raise ValueError(f"machine_id must be 0–{MAX_MACHINE_ID}, got {machine_id}")

        self.machine_id = machine_id
        self._sequence = 0
        self._last_timestamp = -1
        self._lock = threading.Lock()

    def _current_millis(self) -> int:
        """Current time in milliseconds since Unix epoch."""
        return int(time.time() * 1000)

    def _wait_next_millis(self, last_ts: int) -> int:
        """Spin-wait until clock advances to the next millisecond."""
        ts = self._current_millis()
        while ts <= last_ts:
            ts = self._current_millis()
        return ts

    def generate(self) -> int:
        """
        Generate a unique Snowflake ID.

        Returns:
            63-bit integer ID

        Raises:
            RuntimeError: if clock moves backward (should not happen under normal conditions)
        """
        with self._lock:
            ts = self._current_millis()

            if ts < self._last_timestamp:
                raise RuntimeError(
                    f"Clock moved backward by {self._last_timestamp - ts}ms. "
                    "Refusing to generate ID."
                )

            if ts == self._last_timestamp:
                # Same millisecond — increment sequence
                self._sequence = (self._sequence + 1) & MAX_SEQUENCE
                if self._sequence == 0:
                    # Sequence overflow — wait for next ms
                    ts = self._wait_next_millis(self._last_timestamp)
            else:
                # New millisecond — reset sequence
                self._sequence = 0

            self._last_timestamp = ts

            snowflake_id = (
                ((ts - CUSTOM_EPOCH) << TIMESTAMP_SHIFT)
                | (self.machine_id << MACHINE_ID_SHIFT)
                | self._sequence
            )
            return snowflake_id

    @staticmethod
    def parse(snowflake_id: int) -> dict:
        """Decompose a Snowflake ID into its components."""
        sequence = snowflake_id & MAX_SEQUENCE
        machine_id = (snowflake_id >> MACHINE_ID_SHIFT) & MAX_MACHINE_ID
        timestamp_ms = (snowflake_id >> TIMESTAMP_SHIFT) + CUSTOM_EPOCH
        return {
            "timestamp_ms": timestamp_ms,
            "machine_id": machine_id,
            "sequence": sequence,
            "generated_at": time.strftime(
                "%Y-%m-%d %H:%M:%S", time.gmtime(timestamp_ms / 1000)
            ),
        }


class UUIDFallbackGenerator:
    """Fallback ID generator using UUID for single-node / local mode."""

    @staticmethod
    def generate() -> int:
        """Generate a 63-bit ID from UUID4 (truncated)."""
        return uuid.uuid4().int >> 65  # Take top 63 bits


# Module-level singleton
_generator: SnowflakeIDGenerator | None = None
_fallback = UUIDFallbackGenerator()


def init_id_generator(machine_id: int = 0):
    """Initialize the global Snowflake ID generator."""
    global _generator
    _generator = SnowflakeIDGenerator(machine_id)


def generate_id() -> int:
    """Generate a unique ID using Snowflake (or UUID fallback)."""
    if _generator is not None:
        return _generator.generate()
    return _fallback.generate()
