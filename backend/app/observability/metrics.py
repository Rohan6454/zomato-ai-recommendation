from __future__ import annotations

from dataclasses import dataclass, field
from threading import Lock
from typing import Dict


@dataclass
class MetricsRegistry:
    _lock: Lock = field(default_factory=Lock)
    counters: Dict[str, int] = field(default_factory=dict)
    timings_ms_total: Dict[str, float] = field(default_factory=dict)
    timings_count: Dict[str, int] = field(default_factory=dict)

    def inc(self, name: str, value: int = 1) -> None:
        with self._lock:
            self.counters[name] = self.counters.get(name, 0) + value

    def observe_ms(self, name: str, value_ms: float) -> None:
        with self._lock:
            self.timings_ms_total[name] = self.timings_ms_total.get(name, 0.0) + float(value_ms)
            self.timings_count[name] = self.timings_count.get(name, 0) + 1

    def snapshot(self) -> dict:
        with self._lock:
            avg = {}
            for name, total in self.timings_ms_total.items():
                cnt = self.timings_count.get(name, 0)
                avg[name] = (total / cnt) if cnt else 0.0
            return {
                "counters": dict(self.counters),
                "timings_ms_total": dict(self.timings_ms_total),
                "timings_count": dict(self.timings_count),
                "timings_ms_avg": avg,
            }


metrics = MetricsRegistry()

