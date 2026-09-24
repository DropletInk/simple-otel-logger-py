from dataclasses import dataclass


@dataclass
class GpuMetrics:
    id: int
    vendor: str
    name: str

    total_memory_gb: float
    used_memory_gb: float
    utilization_percent: float | None

    @property
    def memory_utilization_percent(self) -> float:
        if self.total_memory_gb == 0:
            return 0.0

        return (
            self.used_memory_gb
            / self.total_memory_gb
            * 100
        )