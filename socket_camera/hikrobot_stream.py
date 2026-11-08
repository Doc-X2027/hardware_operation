"""Preview or capture frames from a Hikrobot GigE Vision camera."""

import argparse
import math
from ctypes import POINTER, cast
from pathlib import Path
import sys

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

import cv2
import numpy as np
from hikrobot import CameraDevice, DeviceManager
from hikrobot.MvImport.CameraParams_header import MV_CC_DEVICE_INFO, MVCC_FLOATVALUE

DEFAULT_WINDOW_SIZE = (1200, 800)
CANVAS_COLOR = (8, 8, 8)
MIN_ZOOM = 0.05
MAX_ZOOM = 50.0
ZOOM_STEP = 1.15


def _ip_address(device: MV_CC_DEVICE_INFO) -> str:
    value = device.SpecialInfo.stGigEInfo.nCurrentIp
    return ".".join(str((value >> shift) & 0xFF) for shift in (24, 16, 8, 0))


def find_camera(ip: str) -> MV_CC_DEVICE_INFO:
    devices = DeviceManager.refresh()
    for index in range(devices.nDeviceNum):
        device = cast(
            devices.pDeviceInfo[index], POINTER(MV_CC_DEVICE_INFO)
        ).contents
        if _ip_address(device) == ip:
            return device
    raise RuntimeError(f"未发现相机 {ip}")


def rgb_frame(camera: CameraDevice, timeout_ms: int) -> np.ndarray | None:
    frame = camera.get_one_frame(timeout_ms)
    if frame is None:
        return None
    raw, info = frame
    rgb = camera.convert_to_rgb(raw, info)
    if rgb is None:
        raise RuntimeError(f"像素格式转换失败: 0x{info.enPixelType:x}")
    return np.frombuffer(rgb, dtype=np.uint8).reshape(info.nHeight, info.nWidth, 3)


def adjust_brightness(image: np.ndarray, brightness: int) -> np.ndarray:
    if brightness == 0:
        return image
    return np.clip(image.astype(np.int16) + brightness, 0, 255).astype(np.uint8)


def camera_float_setting(camera: CameraDevice, name: str) -> MVCC_FLOATVALUE:
    setting = MVCC_FLOATVALUE()
    result = camera._camera.MV_CC_GetFloatValue(name, setting)
    if result != 0:
        raise RuntimeError(f"读取相机参数 {name} 失败 (SDK 错误 0x{result:08x})")
    return setting


def set_camera_float(camera: CameraDevice, name: str, auto_name: str, value: float) -> None:
    setting = camera_float_setting(camera, name)
    if not setting.fMin <= value <= setting.fMax:
        raise ValueError(
            f"{name}={value:g} 超出相机允许范围 "
            f"{setting.fMin:g} 到 {setting.fMax:g}"
        )
    result = camera._camera.MV_CC_SetEnumValueByString(auto_name, "Off")
    if result != 0:
        raise RuntimeError(f"关闭 {auto_name} 失败 (SDK 错误 0x{result:08x})")
    result = camera._camera.MV_CC_SetFloatValue(name, value)
    if result != 0:
        raise RuntimeError(f"设置 {name} 失败 (SDK 错误 0x{result:08x})")
    actual = camera_float_setting(camera, name)
    print(f"{name}: {actual.fCurValue:g}（允许范围 {actual.fMin:g} 到 {actual.fMax:g}）")


def render_on_canvas(
    image: np.ndarray, canvas_size: tuple[int, int], zoom: float
) -> np.ndarray:
    """Render an aspect-preserving image on a dark canvas and clip overflow."""
    canvas_width, canvas_height = canvas_size
    image_height, image_width = image.shape[:2]
    fit_scale = min(canvas_width / image_width, canvas_height / image_height)
    scale = fit_scale * zoom
    offset_x = (canvas_width - image_width * scale) / 2
    offset_y = (canvas_height - image_height * scale) / 2
    transform = np.array(
        [[scale, 0.0, offset_x], [0.0, scale, offset_y]], dtype=np.float64
    )
    interpolation = cv2.INTER_AREA if scale < 1 else cv2.INTER_LINEAR
    return cv2.warpAffine(
        image,
        transform,
        (canvas_width, canvas_height),
        flags=interpolation,
        borderMode=cv2.BORDER_CONSTANT,
        borderValue=CANVAS_COLOR,
    )


def run(
    ip: str,
    output: Path | None,
    timeout_ms: int,
    brightness: int = 0,
    exposure_us: float | None = None,
    gain: float | None = None,
    show_settings: bool = False,
) -> None:
    camera = CameraDevice(find_camera(ip))
    window_name = f"Hikrobot {ip} - Q/Esc quit, S save"
    opened = False
    grabbing = False
    try:
        if not camera.create_handle_and_open():
            raise RuntimeError("打开相机失败（相机可能正被其他程序独占）")
        opened = True

        packet_size = camera._camera.MV_CC_GetOptimalPacketSize()
        if packet_size > 0:
            camera._camera.MV_CC_SetIntValue("GevSCPSPacketSize", packet_size)
        camera._camera.MV_CC_SetEnumValue("TriggerMode", 0)

        if show_settings:
            for name in ("ExposureTime", "Gain"):
                setting = camera_float_setting(camera, name)
                print(
                    f"{name}: 当前 {setting.fCurValue:g}，"
                    f"允许范围 {setting.fMin:g} 到 {setting.fMax:g}"
                )
            return

        if exposure_us is not None:
            set_camera_float(camera, "ExposureTime", "ExposureAuto", exposure_us)
        if gain is not None:
            set_camera_float(camera, "Gain", "GainAuto", gain)

        if not camera.start_grabbing():
            raise RuntimeError("启动取流失败")
        grabbing = True

        if output is None:
            cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
            cv2.resizeWindow(window_name, *DEFAULT_WINDOW_SIZE)
            zoom = [1.0]

            def on_mouse(event: int, _x: int, _y: int, flags: int, _param: object) -> None:
                if event == cv2.EVENT_MOUSEWHEEL:
                    direction = (flags >> 16) & 0xFFFF
                    if direction >= 0x8000:
                        direction -= 0x10000
                    factor = ZOOM_STEP if direction > 0 else 1 / ZOOM_STEP
                    zoom[0] = max(MIN_ZOOM, min(MAX_ZOOM, zoom[0] * factor))
                elif event == cv2.EVENT_MBUTTONDOWN:
                    zoom[0] = 1.0

            cv2.setMouseCallback(window_name, on_mouse)

        while True:
            rgb = rgb_frame(camera, timeout_ms)
            if rgb is None:
                print("等待图像超时，继续重试……")
                continue
            bgr = adjust_brightness(cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR), brightness)

            if output is not None:
                output = output.resolve()
                if not cv2.imwrite(str(output), bgr):
                    raise RuntimeError(f"保存失败: {output}")
                print(f"已保存 {bgr.shape[1]}x{bgr.shape[0]} 图像: {output}")
                return

            _, _, canvas_width, canvas_height = cv2.getWindowImageRect(window_name)
            if canvas_width <= 0 or canvas_height <= 0:
                canvas_width, canvas_height = DEFAULT_WINDOW_SIZE
            canvas = render_on_canvas(
                bgr, (canvas_width, canvas_height), zoom[0]
            )
            cv2.imshow(window_name, canvas)
            key = cv2.waitKey(1) & 0xFF
            if key in (ord("q"), 27):
                return
            if key == ord("s"):
                path = Path(f"camera_{ip}.jpg").resolve()
                cv2.imwrite(str(path), bgr)
                print(f"已保存: {path}")
    finally:
        if grabbing:
            camera.stop_grabbing()
        if opened:
            camera.close_and_destroy()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ip", default="192.168.34.55", help="相机 IPv4 地址")
    parser.add_argument("--output", type=Path, help="抓取一帧并保存；不指定则实时预览")
    parser.add_argument("--timeout", type=int, default=3000, help="单帧超时（毫秒）")
    parser.add_argument("--brightness", type=int, default=0, help="图像亮度偏移，-255 到 255；默认 0")
    parser.add_argument("--exposure-us", type=float, help="设置相机曝光时间（微秒），并关闭自动曝光")
    parser.add_argument("--gain", type=float, help="设置相机增益，并关闭自动增益")
    parser.add_argument("--show-settings", action="store_true", help="显示曝光时间和增益的当前值及允许范围")
    args = parser.parse_args()
    if not -255 <= args.brightness <= 255:
        parser.error("--brightness 必须在 -255 到 255 之间")
    if args.exposure_us is not None and (not math.isfinite(args.exposure_us) or args.exposure_us <= 0):
        parser.error("--exposure-us 必须是大于 0 的有限数")
    if args.gain is not None and (not math.isfinite(args.gain) or args.gain < 0):
        parser.error("--gain 必须是大于或等于 0 的有限数")
    run(args.ip, args.output, args.timeout, args.brightness, args.exposure_us, args.gain, args.show_settings)
