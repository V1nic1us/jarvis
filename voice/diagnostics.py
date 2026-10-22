"""Read-only diagnostics. Presence is distinct from runtime validation."""
import os
import shutil
from pathlib import Path
from audio import list_devices
from platforms import desktop_session
from tts import VoiceError


def _capture_capability(config, ffmpeg_available: bool) -> dict:
    capability = {'available': False, 'backend': config.audio_backend}
    if not ffmpeg_available:
        capability['reason'] = 'ffmpeg ausente'
        return capability
    if config.platform != 'linux':
        capability.update(available=True, reason='ffmpeg presente; gravacao real ainda nao testada')
        return capability
    try:
        list_devices(config)
    except VoiceError as exc:
        capability['reason'] = f'ffmpeg presente, mas o backend de audio nao respondeu: {exc}'
        return capability
    capability.update(
        available=True,
        reason='ffmpeg e enumerador de audio respondem; gravacao real ainda nao testada',
    )
    return capability


def diagnose(config) -> dict:
    session = desktop_session(os.environ)
    dependencies = {}
    for name, executable in [('ffmpeg', config.ffmpeg_exe), ('ffplay', config.ffplay_exe),
                             ('piper', config.piper_exe), ('opencode', config.opencode_bin)]:
        found = shutil.which(executable)
        dependencies[name] = {'available': found is not None, 'path': found,
                              'reason': 'encontrado; runtime nao verificado' if found else f'executavel ausente: {executable}'}
    model = Path(config.piper_model)
    model_exists = model.is_file() and Path(str(model) + '.json').is_file()
    dependencies['piper_model'] = {'available': model_exists, 'path': str(model),
                                  'reason': 'modelo e configuracao presentes' if model_exists else 'modelo .onnx ou configuracao .onnx.json ausente'}
    capabilities = {
        'capture': _capture_capability(config, dependencies['ffmpeg']['available']),
        'tts': {'available': dependencies['piper']['available'] and model_exists and dependencies['ffplay']['available'],
                'backend': config.tts_backend, 'reason': 'presenca de dependencias; sintese nao verificada'},
        'desktop': {'available': False, 'backend': session, 'validation': 'not_run',
                    'reason': 'sem sessao grafica' if session == 'headless' else
                    ('portal Wayland exige autorizacao; controle e AT-SPI precisam de teste na sessao' if session == 'wayland' else
                     'controle X11 exige xdotool; controle e AT-SPI precisam de teste na sessao')
                    if config.platform == 'linux' else 'backend Windows exige validacao de runtime'},
    }
    if config.tts_backend == 'sapi':
        found = shutil.which(config.powershell_exe)
        capabilities['tts'] = {'available': found is not None, 'backend': 'sapi', 'reason': 'SAPI exige teste de runtime Windows'}
    return {'project_root': config.project_root, 'platform': config.platform, 'session': session, 'dependencies': dependencies,
            'capabilities': capabilities}
