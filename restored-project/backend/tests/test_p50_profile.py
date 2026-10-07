from runtime.hardware import HardwareInfo, training_profile, model_profile
from runtime.device_policy import choose_policy
from config.device_profiles import recommend_for_hardware

def p50():
    return HardwareInfo('Windows 11', '3.13', 8, 32.0, True, 'NVIDIA Quadro M1000M', 2.0, False, 300.0, (5,0), 4, 'cpu-or-llama')

def test_p50_cpu_first():
    h=p50(); tp=training_profile(h); policy=choose_policy(h)
    assert tp['device']=='cpu' and tp['amp'] is False
    assert tp['cpu_threads']==6
    assert policy['train_device']=='cpu'
    assert policy['recommended_seq_len']==256

def test_p50_profile_dataset_contract():
    p=recommend_for_hardware(p50())
    assert p['id']=='thinkpad-p50-32gb-2gb'
    assert p['training']['scale']=='small'

def test_p50_model_is_small():
    assert model_profile(p50())['hidden']==256
