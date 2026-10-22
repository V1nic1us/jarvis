import json
import subprocess
import sys
from pathlib import Path
from config import load_config
from diagnostics import diagnose


def test_doctor_reports_missing_dependencies_without_side_effects(tmp_path, monkeypatch):
    monkeypatch.setenv('PATH', str(tmp_path))
    monkeypatch.delenv('DISPLAY', raising=False)
    monkeypatch.delenv('WAYLAND_DISPLAY', raising=False)
    monkeypatch.delenv('XDG_SESSION_TYPE', raising=False)
    cfg = load_config({'JARVIS_PLATFORM': 'linux', 'PIPER_MODEL': str(tmp_path / 'missing.onnx')})
    report = diagnose(cfg)
    assert report['platform'] == 'linux'
    assert report['session'] == 'headless'
    assert report['dependencies']['ffmpeg']['available'] is False
    assert report['dependencies']['piper_model']['available'] is False
    assert report['capabilities']['capture']['available'] is False
    assert list(tmp_path.iterdir()) == []


def test_doctor_marks_pulse_capture_unavailable_when_server_is_unreachable(monkeypatch):
    cfg = load_config({'JARVIS_PLATFORM': 'linux', 'AUDIO_BACKEND': 'pulse'})
    monkeypatch.setattr('diagnostics.shutil.which', lambda executable: f'/usr/bin/{executable}')
    def run(argv, **kwargs):
        if argv == ['ffmpeg', '-hide_banner', '-demuxers']:
            return subprocess.CompletedProcess(argv, 0, '', ' D d pulse Pulse audio input\n')
        assert argv == ['pactl', '--format=json', 'list', 'sources']
        return subprocess.CompletedProcess(argv, 1, '', 'Connection refused')
    monkeypatch.setattr('audio.subprocess.run', run)

    capture = diagnose(cfg)['capabilities']['capture']

    assert capture['available'] is False
    assert 'Connection refused' in capture['reason']


def test_doctor_reports_pulse_server_reachable_without_claiming_capture_tested(monkeypatch):
    cfg = load_config({'JARVIS_PLATFORM': 'linux', 'AUDIO_BACKEND': 'pulse'})
    monkeypatch.setattr('diagnostics.shutil.which', lambda executable: f'/usr/bin/{executable}')
    def run(argv, **kwargs):
        if argv == ['ffmpeg', '-hide_banner', '-demuxers']:
            return subprocess.CompletedProcess(argv, 0, '', ' D d pulse Pulse audio input\n')
        assert argv == ['pactl', '--format=json', 'list', 'sources']
        return subprocess.CompletedProcess(argv, 0, '[{"name":"mic usb"}]', '')
    monkeypatch.setattr('audio.subprocess.run', run)

    capture = diagnose(cfg)['capabilities']['capture']

    assert capture['available'] is True
    assert capture['backend'] == 'pulse'
    assert 'gravacao real ainda nao testada' in capture['reason']


def test_doctor_marks_capture_unavailable_when_ffmpeg_lacks_backend_demuxer(monkeypatch):
    cfg = load_config({'JARVIS_PLATFORM': 'linux', 'AUDIO_BACKEND': 'pulse'})
    monkeypatch.setattr('diagnostics.shutil.which', lambda executable: f'/usr/bin/{executable}')
    def run(argv, **kwargs):
        if argv == ['ffmpeg', '-hide_banner', '-demuxers']:
            return subprocess.CompletedProcess(argv, 0, '', ' D d alsa ALSA audio input\n')
        assert argv == ['pactl', '--format=json', 'list', 'sources']
        return subprocess.CompletedProcess(argv, 0, '[{"name":"mic usb"}]', '')
    monkeypatch.setattr('audio.subprocess.run', run)

    capture = diagnose(cfg)['capabilities']['capture']

    assert capture['available'] is False
    assert 'ffmpeg nao disponibiliza entrada pulse' in capture['reason']


def test_doctor_checks_alsa_input_support_and_device_enumerator(monkeypatch):
    cfg = load_config({'JARVIS_PLATFORM': 'linux', 'AUDIO_BACKEND': 'alsa'})
    monkeypatch.setattr('diagnostics.shutil.which', lambda executable: f'/usr/bin/{executable}')
    calls = []
    def run(argv, **kwargs):
        calls.append(argv)
        if argv == ['ffmpeg', '-hide_banner', '-demuxers']:
            return subprocess.CompletedProcess(argv, 0, '', ' D d alsa ALSA audio input\n')
        assert argv == ['arecord', '-L']
        return subprocess.CompletedProcess(argv, 0, 'default\n    Default PCM\n', '')
    monkeypatch.setattr('audio.subprocess.run', run)

    capture = diagnose(cfg)['capabilities']['capture']

    assert capture['available'] is True
    assert capture['backend'] == 'alsa'
    assert 'gravacao real ainda nao testada' in capture['reason']
    assert calls == [['ffmpeg', '-hide_banner', '-demuxers'], ['arecord', '-L']]


def test_doctor_cli_prints_json_without_starting_agent():
    proc = subprocess.run([sys.executable, str(Path(__file__).resolve().parents[1] / 'loop.py'), '--doctor'], capture_output=True, text=True, timeout=10)
    assert proc.returncode == 0
    assert json.loads(proc.stdout)['platform'] == 'linux'


def test_doctor_wayland_reports_authorization_requirement(monkeypatch):
    monkeypatch.setenv('WAYLAND_DISPLAY','wayland-test')
    cfg=load_config({'JARVIS_PLATFORM':'linux'})
    desktop=diagnose(cfg)['capabilities']['desktop']
    assert desktop['backend']=='wayland'
    assert desktop['validation']=='not_run'
    assert 'autorizacao' in desktop['reason']
    assert 'nao implementado' not in desktop['reason']


def test_doctor_x11_reports_runtime_requirement(monkeypatch):
    monkeypatch.delenv('WAYLAND_DISPLAY',raising=False)
    monkeypatch.setenv('XDG_SESSION_TYPE','x11')
    monkeypatch.setenv('DISPLAY',':99')
    cfg=load_config({'JARVIS_PLATFORM':'linux'})
    desktop=diagnose(cfg)['capabilities']['desktop']
    assert desktop['validation']=='not_run'
    assert 'xdotool' in desktop['reason']
