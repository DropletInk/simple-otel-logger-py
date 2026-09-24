# import amdsmi

# from pylog.gpu.models import GpuMetrics


# class AmdBackend:
#     def __init__(self) -> None:
#         amdsmi.amdsmi_init()

#     def collect(self) -> list[GpuMetrics]:
#         metrics = []

#         devices = amdsmi.amdsmi_get_processor_handles()

#         for i, device in enumerate(devices):
#             name = amdsmi.amdsmi_get_gpu_asic_info(device)[
#                 "market_name"
#             ]

#             total_memory = amdsmi.amdsmi_get_gpu_memory_total(
#                 device,
#                 amdsmi.AmdSmiMemoryType.VRAM,
#             )

#             used_memory = amdsmi.amdsmi_get_gpu_memory_usage(
#                 device,
#                 amdsmi.AmdSmiMemoryType.VRAM,
#             )

#             utilization = amdsmi.amdsmi_get_gpu_busy_percent(
#                 device
#             )

#             metrics.append(
#                 GpuMetrics(
#                     id=i,
#                     vendor="amd",
#                     name=name,
#                     total_memory_gb=total_memory / (1024 ** 3),
#                     used_memory_gb=used_memory / (1024 ** 3),
#                     utilization_percent=utilization,
#                 )
#             )

#         return metrics

#     def close(self) -> None:
#         amdsmi.amdsmi_shut_down()