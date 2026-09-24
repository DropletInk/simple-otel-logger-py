import pynvml

from pylog.gpu.models import GpuMetrics


class NvidiaBackend:
    def __init__(self) -> None:
        pynvml.nvmlInit()

    def collect(self) -> list[GpuMetrics]:
        metrics = []

        count = pynvml.nvmlDeviceGetCount()

        for i in range(count):
            handle = pynvml.nvmlDeviceGetHandleByIndex(i)
            name = pynvml.nvmlDeviceGetName(handle)

            if isinstance(name, bytes):
                name = name.decode()

            memory = pynvml.nvmlDeviceGetMemoryInfo(handle)
            utilization = pynvml.nvmlDeviceGetUtilizationRates(
                handle
            )

            metrics.append(
                GpuMetrics(
                    id=i,
                    vendor="nvidia",
                    name=name,
                    total_memory_gb=memory.total / (1024 ** 3),
                    used_memory_gb=memory.used / (1024 ** 3),
                    utilization_percent=utilization.gpu,
                )
            )

        return metrics

    def close(self) -> None:
        pynvml.nvmlShutdown()