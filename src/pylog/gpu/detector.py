import shutil
import pynvml
#import rocm_smi

def detect_gpu_vendor() -> str | None:
    # NVIDIA
    try:
        pynvml.nvmlInit()

        if pynvml.nvmlDeviceGetCount() > 0:
            pynvml.nvmlShutdown()
            return "nvidia"

        pynvml.nvmlShutdown()

    except Exception:
        pass

    # Intel
    if shutil.which("xpu-smi"):
        return "intel"

    # # AMD
    # try:
    #     _ = rocm_smi
    #     return "amd"
    # except ImportError:
    #     pass

    return None