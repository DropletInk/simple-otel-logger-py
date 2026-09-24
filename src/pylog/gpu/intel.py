# import csv
# import io
# import shutil
# import subprocess

# from pylog.gpu.models import GpuMetrics


# class IntelBackend:
#     def __init__(self) -> None:
#         self._xpu_smi = shutil.which("xpu-smi")

#         if self._xpu_smi is None:
#             raise RuntimeError(
#                 "xpu-smi is required for Intel GPU monitoring"
#             )

#     def collect(self) -> list[GpuMetrics]:
#         metrics = []

#         result = subprocess.run(
#             [
#                 self._xpu_smi,
#                 "--query-gpu",
#                 "index,name,utilization.gpu,memory.used,memory.total",
#                 "--format=csv,noheader,nounits",
#             ],
#             capture_output=True,
#             text=True,
#             check=True,
#             timeout=2,
#         )

#         reader = csv.reader(
#             io.StringIO(result.stdout)
#         )

#         for row in reader:
#             if len(row) != 5:
#                 continue

#             device_id = int(row[0].strip())
#             name = row[1].strip()

#             utilization = self._parse_float(row[2])
#             used_memory = self._parse_float(row[3])
#             total_memory = self._parse_float(row[4])

#             if used_memory is None or total_memory is None:
#                 continue

#             metrics.append(
#                 GpuMetrics(
#                     id=device_id,
#                     vendor="intel",
#                     name=name,
#                     total_memory_gb=total_memory / 1024,
#                     used_memory_gb=used_memory / 1024,
#                     utilization_percent=utilization,
#                 )
#             )

#         return metrics

#     @staticmethod
#     def _parse_float(value: str) -> float | None:
#         value = value.strip()

#         if not value or value.upper() == "N/A":
#             return None

#         try:
#             return float(value)
#         except ValueError:
#             return None

#     def close(self) -> None:
#         pass