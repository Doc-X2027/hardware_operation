"""Select the configured USB camera by hardware identity on Linux."""
import json
from pathlib import Path
import sys


def select_device(index=None):
    if not sys.platform.startswith('linux'):
        if index is None:
            raise RuntimeError('Windows 请显式指定 --index；Linux 索引不能直接用于 Windows')
        return index, f'手动索引 {index}（设备身份未验证）'
    config = json.loads(Path(__file__).with_name('config.json').read_text())
    candidates = []
    for node in sorted(Path('/sys/class/video4linux').glob('video*')):
        if (node / 'index').read_text().strip() != '0':
            continue
        for parent in (node / 'device').resolve().parents:
            if (parent / 'idVendor').exists():
                identity = {key: (parent / key).read_text().strip() if (parent / key).exists() else ''
                            for key in ('idVendor', 'idProduct', 'serial')}
                if all(identity[key] == config[key] for key in identity):
                    candidates.append((int(node.name[5:]), (node / 'name').read_text().strip(), identity))
                break
    if index is not None:
        candidates = [entry for entry in candidates if entry[0] == index]
    if len(candidates) != 1:
        raise RuntimeError(f'目标外接相机未找到或不唯一：{config}；不会回退到内置摄像头。请检查连接和 --index')
    number, name, identity = candidates[0]
    return f'/dev/video{number}', f'{name}; {identity}; /dev/video{number}'


def frame_stats(frame):
    import cv2
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) if frame.ndim == 3 else frame
    low, high = int(gray.min()), int(gray.max())
    mean, std = float(gray.mean()), float(gray.std())
    # A conservative diagnostic, not a device-identity or image-quality classifier.
    suspicious = high <= 5 or std < 1.0
    return suspicious, f'灰度 min={low}, max={high}, mean={mean:.2f}, std={std:.2f}'
