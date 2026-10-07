from runtime.hardware import HardwareInfo
from runtime.device_policy import gguf_offload_policy


def test_gpu_memory_fields_are_semantically_ordered():
    h = HardwareInfo(os="Windows", python="3.11.9", cpu_cores=8, ram_gb=32, gpu_available=True, gpu_name="NVIDIA Quadro M1000M", vram_gb=2.0, torch_cuda=True, disk_free_gb=100.0, cuda_capability=(5,0), physical_cores=4, backend_hint="cuda", gpu_mem_used_gb=0.50, gpu_mem_free_gb=1.50)
    assert h.gpu_mem_used_gb < h.gpu_mem_free_gb
    p = gguf_offload_policy(h, mode="auto", total_layers=24)
    assert p["n_gpu_layers"] == 24
