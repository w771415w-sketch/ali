from runtime.hardware import HardwareInfo, training_profile

def hw(free, cuda=True):
    return HardwareInfo('Windows', '3.11', 8, 32, True, 'NVIDIA Quadro M1000M', 2.0, cuda, 20, (5,0), 4, 'cuda' if cuda else 'cpu', gpu_mem_used_gb=2.0-free, gpu_mem_free_gb=free, cuda_self_test=cuda)

def test_auto_uses_gpu_when_free_vram_is_sufficient():
    p=training_profile(hw(1.20), 'auto')
    assert p['device']=='cuda' and p['seq_len']==192

def test_auto_falls_back_to_cpu_when_vram_is_low():
    p=training_profile(hw(0.40), 'auto')
    assert p['device']=='cpu'

def test_forced_gpu_rejects_unusable_cuda():
    import pytest
    with pytest.raises(RuntimeError):
        training_profile(hw(0.40, cuda=False), 'gpu')
