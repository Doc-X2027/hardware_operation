"""Linux GigE Vision acquisition using Aravis 0.8; run via run.sh."""
import argparse
import json
from pathlib import Path
import sys
import time


def decode_frame(buffer, pixel_format, cv2, np):
    width, height = buffer.get_image_width(), buffer.get_image_height()
    data = np.frombuffer(bytes(buffer.get_data()), dtype=np.uint8)
    channels = 3 if pixel_format in ('RGB8', 'BGR8', 'RGB8Packed', 'BGR8Packed') else 1
    if data.size != width * height * channels:
        raise RuntimeError('图像长度不匹配；当前仅支持无填充的 Mono8、Bayer8、RGB8/BGR8，不支持分块/打包高位深格式')
    frame = data.reshape((height, width, channels) if channels == 3 else (height, width))
    if pixel_format == 'Mono8':
        return frame.copy()
    if pixel_format in ('RGB8', 'RGB8Packed'):
        return cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    if pixel_format in ('BGR8', 'BGR8Packed'):
        return frame.copy()
    # OpenCV's legacy two-letter names are opposite to the full PFNC pattern.
    # Use constants available in Ubuntu 22.04's OpenCV 4.5.4.
    codes = {'BayerRG8': cv2.COLOR_BayerBG2BGR,
             'BayerGR8': cv2.COLOR_BayerGB2BGR,
             'BayerGB8': cv2.COLOR_BayerGR2BGR,
             'BayerBG8': cv2.COLOR_BayerRG2BGR}
    if pixel_format in codes:
        return cv2.cvtColor(frame, codes[pixel_format])
    raise RuntimeError(f'不支持像素格式 {pixel_format}；请使用 --pixel-format Mono8 或设备支持的 Bayer8 格式')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, default=Path(__file__).with_name('config.json'))
    parser.add_argument('--ip', help='相机 IP，覆盖配置文件')
    parser.add_argument('--list', action='store_true', help='列出发现的相机')
    parser.add_argument('--headless', action='store_true', help='无窗口取流')
    parser.add_argument('--frames', type=int, default=0, help='成功采集指定帧数后退出；0 为持续取流')
    parser.add_argument('--output', type=Path, help='保存首帧并退出')
    parser.add_argument('--pixel-format', help='临时设置像素格式，如 Mono8、BayerRG8；退出恢复')
    parser.add_argument('--simulate', action='store_true', help='使用 Aravis 模拟相机，仅测试软件')
    args = parser.parse_args()
    if args.frames < 0:
        parser.error('--frames 不能小于 0')
    config = json.loads(args.config.read_text())
    for key in ('timeout_ms', 'max_failures', 'buffers'):
        if type(config[key]) is not int or config[key] <= 0:
            raise ValueError(f'配置 {key} 必须为正整数')
    import gi
    gi.require_version('Aravis', '0.8')
    from gi.repository import Aravis
    import cv2
    import numpy as np

    if args.simulate:
        Aravis.enable_interface('Fake')
    if args.list:
        Aravis.update_device_list()
        for i in range(Aravis.get_n_devices()):
            print(Aravis.get_device_id(i), Aravis.get_device_address(i))
        print(f'发现 {Aravis.get_n_devices()} 台设备')
        return 0
    target = 'Fake_1' if args.simulate else (args.ip or config['camera_ip'])
    print(f'连接 {target}', flush=True)
    camera = Aravis.Camera.new(target)
    if camera is None:
        raise RuntimeError(f'无法打开 {target}')
    print(f'{camera.get_vendor_name()} / {camera.get_model_name()} / SN {camera.get_device_serial_number()}')
    original = {}
    started = False
    stream = None
    preview = not args.headless and args.output is None
    window = None
    try:
        # Save settings before changing them; do not persist a camera user set.
        for feature in ('TriggerMode', 'AcquisitionMode'):
            original[feature] = camera.get_string(feature)
        if args.pixel_format:
            original['PixelFormat'] = camera.get_pixel_format_as_string()
            camera.set_pixel_format_from_string(args.pixel_format)
        camera.set_string('TriggerMode', 'Off')
        camera.set_acquisition_mode(Aravis.AcquisitionMode.CONTINUOUS)
        pixel_format = camera.get_pixel_format_as_string()
        print(f'ROI {camera.get_region()}, PixelFormat {pixel_format}', flush=True)
        stream = camera.create_stream(None, None)
        for _ in range(config['buffers']):
            stream.push_buffer(Aravis.Buffer.new_allocate(camera.get_payload()))
        if preview:
            from preview import Preview
            window = Preview(target)
        camera.start_acquisition()
        started = True
        count = failures = 0
        start = time.monotonic()
        while True:
            buffer = stream.timeout_pop_buffer(config['timeout_ms'] * 1000)
            frame = None
            try:
                if buffer is not None and buffer.get_status() == Aravis.BufferStatus.SUCCESS:
                    frame = decode_frame(buffer, pixel_format, cv2, np)
            finally:
                if buffer is not None:
                    stream.push_buffer(buffer)
            if frame is None:
                failures += 1
                print(f'取帧超时或无效 ({failures}/{config["max_failures"]})', file=sys.stderr)
                if failures >= config['max_failures']:
                    raise RuntimeError('连续取帧失败；检查有线网段、设备占用、防火墙和 GigE 包大小')
            else:
                failures = 0
                count += 1
                if count == 1 or count % 30 == 0:
                    print(f'帧 {count}: {frame.shape[1]}x{frame.shape[0]}, 平均 {count / (time.monotonic()-start):.1f} FPS', flush=True)
                if args.output:
                    args.output.parent.mkdir(parents=True, exist_ok=True)
                    if not cv2.imwrite(str(args.output), frame):
                        raise RuntimeError(f'保存失败: {args.output}')
                    print(f'已保存 {args.output}')
                    break
                if args.frames and count >= args.frames:
                    break
            if window is not None and not window.update(frame):
                break
    finally:
        try:
            if started:
                camera.stop_acquisition()
        finally:
            for feature, value in reversed(list(original.items())):
                try:
                    camera.set_string(feature, value)
                except Exception as exc:
                    print(f'恢复 {feature} 失败: {exc}', file=sys.stderr)
            if window is not None:
                window.close()
            stream = None
            camera = None
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print('已停止')
        sys.exit(130)
    except Exception as exc:
        print(f'错误: {exc}', file=sys.stderr)
        sys.exit(1)
