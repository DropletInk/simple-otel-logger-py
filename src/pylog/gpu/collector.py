from pylog.gpu.models import GpuMetrics
from pylog.gpu.detector import detect_gpu_vendor


class GpuCollector:
    def __init__(self) -> None:
        print(".......GpuCollector.......")
        self.backend = self._create_backend()

    def _create_backend(self):
        vendor = detect_gpu_vendor()
        print(f"..............vendor: {vendor}")
        if vendor == "nvidia":
            from pylog.gpu.nvidia import NvidiaBackend

            return NvidiaBackend()

        if vendor == "amd":
            from pylog.gpu.amd import AmdBackend

            return AmdBackend()

        if vendor == "intel":
            from pylog.gpu.intel import IntelBackend

            return IntelBackend()

        return None

    def collect(self) -> list[GpuMetrics]:
        print(f"..............self.backend: {self.backend}")
        if self.backend is None:
            return []

        return self.backend.collect()