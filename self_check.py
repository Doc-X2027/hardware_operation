"""Hardware checks without robot power or motion commands."""

import argparse
from ctypes import POINTER, cast
import json
import math
import struct
import os
from pathlib import Path
import socket
import subprocess
import sys


ROOT = Path(__file__).resolve().parent


def result(name, status, detail):
    return {"item": name, "status": status, "detail": str(detail)}


def tcp_probe(name, host, port, timeout):
    try:
        with socket.create_connection((host, port), timeout=timeout):
            pass
        return result(name, "PASS", f"{host}:{port} 可连接")
    except OSError as exc:
        source = ""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as route:
                route.connect((host, port))
                source = f"；本机路由选择 {route.getsockname()[0]}"
        except OSError:
            pass
        return result(name, "FAIL", f"{host}:{port} 连接失败: {exc}{source}")


def gige_probe(ip, timeout):
    try:
        vendor = ROOT / "socket_camera"
        if str(vendor) not in sys.path:
            sys.path.insert(0, str(vendor))
        from hikrobot import CameraDevice, DeviceManager
        from hikrobot.MvImport.CameraParams_header import MV_CC_DEVICE_INFO, MVCC_ENUMVALUE

        devices = DeviceManager.refresh()
        found = []
        target = None
        for index in range(devices.nDeviceNum):
            device = cast(devices.pDeviceInfo[index], POINTER(MV_CC_DEVICE_INFO)).contents
            value = device.SpecialInfo.stGigEInfo.nCurrentIp
            address = ".".join(str((value >> shift) & 255) for shift in (24, 16, 8, 0))
            found.append(address)
            if address == ip:
                target = device
        if target is None:
            return result("GigE 相机", "FAIL", f"未发现 {ip}；发现的 IP: {found}")
        camera = CameraDevice(target)
        opened = False
        grabbing = False
        original_trigger_mode = None
        trigger_changed = False
        try:
            if not camera.create_handle_and_open():
                return result("GigE 相机", "FAIL", f"发现 {ip}，但无法打开设备")
            opened = True
            setting = MVCC_ENUMVALUE()
            if camera._camera.MV_CC_GetEnumValue("TriggerMode", setting) != 0:
                return result("GigE 相机", "FAIL", f"打开 {ip} 成功，但无法读取触发模式")
            original_trigger_mode = setting.nCurValue
            if original_trigger_mode != 0:
                if camera._camera.MV_CC_SetEnumValue("TriggerMode", 0) != 0:
                    return result("GigE 相机", "FAIL", f"打开 {ip} 成功，但无法切换到连续取流")
                trigger_changed = True
            if not camera.start_grabbing():
                return result("GigE 相机", "FAIL", f"打开 {ip} 成功，但无法开始取流")
            grabbing = True
            frame = camera.get_one_frame(round(timeout * 1000))
            if frame is None:
                return result("GigE 相机", "FAIL", f"发现并打开 {ip}，但取帧超时；请检查触发模式")
            _, info = frame
            return result("GigE 相机", "PASS", f"{ip} 取帧成功，图像 {info.nWidth}x{info.nHeight}")
        finally:
            try:
                if grabbing:
                    camera.stop_grabbing()
            finally:
                if opened:
                    try:
                        if trigger_changed and camera._camera.MV_CC_SetEnumValue("TriggerMode", original_trigger_mode) != 0:
                            raise RuntimeError("取帧后恢复相机触发模式失败")
                    finally:
                        camera.close_and_destroy()
    except Exception as exc:
        return result("GigE 相机", "FAIL", f"MVS 检查失败（发现、打开或取帧阶段）: {exc}")


def usb_probe(index=None):
    try:
        import cv2

        from usb_camera_linux.device import select_device, frame_stats
        source, identity = select_device(index)
        cap = cv2.VideoCapture(source, cv2.CAP_V4L2) if sys.platform.startswith("linux") else cv2.VideoCapture(source)
        try:
            if not cap.isOpened():
                return result("USB 相机", "FAIL", f"设备索引 {index} 无法打开")
            for _ in range(15):
                cap.read()
            ok, frame = cap.read()
            if not ok or frame is None or frame.size == 0:
                return result("USB 相机", "FAIL", f"设备索引 {index} 无法取帧")
            suspicious, stats = frame_stats(frame)
            return result("USB 相机", "FAIL" if suspicious else "PASS",
                          f"{identity}；图像 {frame.shape[1]}x{frame.shape[0]}；{stats}"
                          + ("；画面接近全黑或缺少变化，需排查" if suspicious else "；画面有灰度变化，不代表成像质量已验证"))
        finally:
            cap.release()
    except Exception as exc:
        return result("USB 相机", "FAIL", f"取帧失败: {exc}")


def force_probe(timeout):
    if os.name != "nt" or sys.version_info[:2] != (3, 12) or struct.calcsize("P") != 8:
        return result("力传感器", "SKIP", "现有模块要求 Windows x64 / Python 3.12")
    code = (
        "import json; from force_sensor import ForceSensor; "
        "s=ForceSensor(zero_calib=False); "
        "\ntry:\n print(json.dumps(list(s.read_one())))"
        "\nfinally:\n s.close()"
    )
    try:
        process = subprocess.run(
            [sys.executable, "-c", code], cwd=ROOT,
            capture_output=True, text=True, timeout=timeout, check=False
        )
        if process.returncode != 0:
            lines = [line.strip() for line in (process.stderr or process.stdout).splitlines() if line.strip()]
            diagnosis = [
                line for line in lines
                if "DaqError:" in line or line.startswith(("Status Code:", "Device Specified:"))
            ]
            if not diagnosis:
                diagnosis = [line for line in lines if "UserWarning:" not in line]
                diagnosis = diagnosis[-1:]
            return result("力传感器", "FAIL", " | ".join(diagnosis) or f"退出码 {process.returncode}")
        values = json.loads(process.stdout.strip().splitlines()[-1])
        if len(values) != 3:
            raise ValueError(f"预期 3 个轴，得到 {values}")
        return result("力传感器", "PASS", f"Fx/Fy/Fz (N): {values}")
    except subprocess.TimeoutExpired:
        return result("力传感器", "FAIL", f"读取超过 {timeout:g} 秒")
    except (ValueError, IndexError, OSError) as exc:
        return result("力传感器", "FAIL", f"读数格式异常: {exc}")


def aravis_environment():
    """Match run.sh; use system Python for distribution GI bindings."""
    env = os.environ.copy()
    lib = ROOT / "socket_camera_linux/lib/usr/lib/x86_64-linux-gnu"
    if lib.is_dir():
        for key, path in (("GI_TYPELIB_PATH", lib / "girepository-1.0"),
                          ("LD_LIBRARY_PATH", lib)):
            env[key] = str(path) + (os.pathsep + env[key] if env.get(key) else "")
    return env


def isolated_probe(name, command, timeout, env=None, structured=False):
    """Keep native SDK output/crashes and blocking reads outside the reporter."""
    try:
        process = subprocess.run(command, cwd=ROOT, env=env, capture_output=True,
                                 text=True, encoding="utf-8", errors="replace",
                                 timeout=timeout, check=False)
    except subprocess.TimeoutExpired:
        return result(name, "FAIL", f"检查超过 {timeout:g} 秒，已终止子进程；相机参数恢复无法保证")
    except OSError as exc:
        return result(name, "FAIL", f"无法启动检查: {exc}")
    if structured and process.returncode == 0:
        for line in reversed(process.stdout.splitlines()):
            if line.startswith("SELF_CHECK_RESULT="):
                try:
                    check = json.loads(line.split("=", 1)[1])
                    if check["status"] not in ("PASS", "FAIL", "SKIP"):
                        raise ValueError("未知状态")
                    return result(name, check["status"], check["detail"])
                except (ValueError, KeyError, TypeError):
                    break
        return result(name, "FAIL", "子进程未返回有效检查结果")
    output = (process.stdout + "\n" + process.stderr).strip()
    # stream.py reports restoration problems to stderr without changing exit code.
    failed = process.returncode != 0 or ("恢复 " in process.stderr and "失败" in process.stderr)
    return result(name, "FAIL" if failed else "PASS",
                  f"退出码 {process.returncode}；{output[-3000:]}")


def worker_probe(kind, args):
    try:
        if kind == "usb":
            return usb_probe((args.usb_index or [None])[0])
        if kind == "mvs":
            return gige_probe(args.gige_ip, args.timeout)
        if kind == "opencv":
            import cv2
            import numpy
            return result(kind, "PASS", f"OpenCV {cv2.__version__}, NumPy {numpy.__version__}")
        if kind == "aravis-deps":
            import gi
            gi.require_version("Aravis", "0.8")
            from gi.repository import Aravis
            import cv2
            import numpy
            return result(kind, "PASS", "Aravis 0.8 / GI / OpenCV / NumPy 可加载；/usr/bin/python3")
        if kind == "mvs-deps":
            sys.path.insert(0, str(ROOT / "socket_camera"))
            import hikrobot
            import cv2
            import numpy
            return result(kind, "PASS", "MVS 封装 / OpenCV / NumPy 可加载")
        if kind == "preview":
            if sys.platform.startswith("linux"):
                import gi
                import cairo
                gi.require_version("Gtk", "3.0")
                from gi.repository import Gtk
                if not Gtk.init_check()[0]:
                    return result(kind, "FAIL", "GTK 无法连接图形桌面；可使用拍摄或无窗口取流")
                return result(kind, "PASS", "GTK 3 / Cairo 可加载且显示服务可连接；未验证鼠标事件")
            import cv2
            cv2.namedWindow("Self check")
            try:
                cv2.waitKey(1)
            finally:
                cv2.destroyWindow("Self check")
            return result(kind, "PASS", "OpenCV 窗口创建成功；未验证鼠标事件")
        raise ValueError(f"未知检查 {kind}")
    except Exception as exc:
        return result(kind, "FAIL", f"{type(exc).__name__}: {exc}")


def main():
    parser = argparse.ArgumentParser(description="硬件自检；不让机械臂上电或运动，不做力传感器零点校准")
    parser.add_argument("--offline", action="store_true", help="检查文件及依赖，不连接硬件")
    for device in ("robot", "gige", "usb", "force"):
        parser.add_argument(f"--skip-{device}", action="store_true", help=f"跳过 {device} 检查")
    parser.add_argument("--check-preview", action="store_true", help="额外检查图形预览环境（需要桌面）")
    parser.add_argument("--check-camera-service", action="store_true", help="检查可选 TCP 相机服务端口")
    parser.add_argument("--json", action="store_true", help="标准输出仅包含 JSON 结果数组")
    parser.add_argument("--robot-ip", default="192.168.34.10")
    parser.add_argument("--robot-port", type=int, default=30004)
    parser.add_argument("--socket-host", default="127.0.0.1")
    parser.add_argument("--socket-port", type=int, default=8888)
    parser.add_argument("--gige-ip", default="192.168.34.55")
    parser.add_argument("--gige-backend", choices=("auto", "mvs", "aravis"), default="auto")
    parser.add_argument("--usb-index", type=int, nargs="+", default=None, help="显式设备索引；Linux 默认按外接相机身份匹配，Windows 需指定")
    parser.add_argument("--timeout", type=float, default=5.0, help="每个网络/依赖/硬件检查的超时秒数")
    parser.add_argument("--worker", choices=("usb", "mvs", "opencv", "aravis-deps", "mvs-deps", "preview"), help=argparse.SUPPRESS)
    args = parser.parse_args()
    if not math.isfinite(args.timeout) or args.timeout <= 0:
        parser.error("--timeout 必须为有限正数")
    if any(index < 0 for index in (args.usb_index or [])):
        parser.error("--usb-index 必须大于或等于 0")
    if any(not 1 <= port <= 65535 for port in (args.robot_port, args.socket_port)):
        parser.error("端口必须在 1～65535 之间")
    if args.worker:
        print("SELF_CHECK_RESULT=" + json.dumps(worker_probe(args.worker, args), ensure_ascii=False))
        return 0

    backend = args.gige_backend
    if backend == "auto":
        backend = "aravis" if sys.platform.startswith("linux") else "mvs"
    required = [
        "aubo_robot/control.py", "socket_camera/hikvision.py",
        "socket_camera/hikrobot_stream.py", "socket_camera_linux/run.sh",
        "socket_camera_linux/stream.py", "socket_camera_linux/preview.py", "socket_camera_linux/config.json",
        "usb_camera/control.py", "usb_camera/preview.py", "usb_camera/requirements.txt",
        "usb_camera_linux/device.py", "usb_camera_linux/config.json",
        "usb_camera/device.py", "usb_camera/config.json", "usb_camera_linux/control.py", "usb_camera_linux/preview.py", "usb_camera_linux/requirements.txt",
        "force_sensor/control.py", "force_sensor/force_sensor.py",
    ]
    if os.name == "nt":
        required += ["aubo_robot/pyaubo_sdk.cp312-win_amd64.pyd",
                     "force_sensor/legacy/force_sensor.cpython-312.pyc", "force_sensor/native/Art_DAQ.dll"]
    missing = [path for path in required if not (ROOT / path).is_file()]
    checks = [result("仓库文件", "FAIL" if missing else "PASS", missing or "当前平台所需入口文件齐全"),
              result("运行环境", "PASS", f"{sys.platform}, Python {sys.version.split()[0]}, {struct.calcsize('P') * 8} 位；{sys.executable}；GigE={backend}")]

    def worker(name, kind, system=False, extra=()):
        python = "/usr/bin/python3" if system else sys.executable
        return isolated_probe(name, [python, str(ROOT / "self_check.py"), "--worker", kind,
                                     "--timeout", str(args.timeout), *extra], args.timeout,
                              aravis_environment() if system else None, structured=True)

    if not args.skip_usb:
        checks.append(worker("USB 依赖", "opencv"))
    if not args.skip_gige:
        if backend == "aravis" and not sys.platform.startswith("linux"):
            checks.append(result("GigE 依赖", "FAIL", "仓库 Aravis 入口仅支持 Linux"))
        else:
            checks.append(worker("GigE 依赖", backend + "-deps", system=backend == "aravis"))
    if args.check_preview:
        checks.append(worker("预览环境", "preview"))
    compatible = os.name == "nt" and sys.version_info[:2] == (3, 12) and struct.calcsize("P") == 8
    checks.append(result("Windows SDK 平台", "PASS" if compatible else "SKIP",
                         "Windows x64 / Python 3.12 匹配；不代表 SDK 可登录或驱动可用" if compatible
                         else "仓库 AUBO/力传感器二进制需要 Windows x64 / Python 3.12；RPC 端口仍可检查"))
    checks.append(result("AUBO RPC", "SKIP", "离线模式或 --skip-robot")
                  if args.offline or args.skip_robot else tcp_probe("AUBO RPC", args.robot_ip, args.robot_port, args.timeout))
    checks.append(tcp_probe("TCP 相机服务", args.socket_host, args.socket_port, args.timeout)
                  if args.check_camera_service and not args.offline else result("TCP 相机服务", "SKIP", "离线模式或未指定 --check-camera-service"))
    if args.offline or args.skip_gige:
        checks.append(result("GigE 相机", "SKIP", "离线模式或 --skip-gige"))
    elif any(c["item"] == "GigE 依赖" and c["status"] == "FAIL" for c in checks):
        checks.append(result("GigE 相机", "SKIP", "GigE 依赖检查失败"))
    elif backend == "aravis":
        checks.append(isolated_probe("GigE 相机", ["/usr/bin/python3", str(ROOT / "socket_camera_linux/stream.py"),
                      "--ip", args.gige_ip, "--headless", "--frames", "1"], args.timeout, aravis_environment()))
    else:
        checks.append(worker("GigE 相机", "mvs", extra=("--gige-ip", args.gige_ip)))
    for index in dict.fromkeys(args.usb_index or [None]):
        name = f"USB 相机 [{index}]" if index is not None else "USB 相机 [配置目标]"
        checks.append(result(name, "SKIP", "离线模式或 --skip-usb") if args.offline or args.skip_usb
                      else worker(name, "usb", extra=("--usb-index", str(index)) if index is not None else ()))
    checks.append(result("力传感器", "SKIP", "离线模式或 --skip-force")
                  if args.offline or args.skip_force else force_probe(args.timeout))
    if args.json:
        print(json.dumps(checks, ensure_ascii=False, indent=2))
    else:
        for check in checks:
            print(f"[{check['status']}] {check['item']}: {check['detail']}")
        print("汇总: " + ", ".join(f"{status}={sum(c['status'] == status for c in checks)}" for status in ("PASS", "FAIL", "SKIP")))
    return 1 if any(check["status"] == "FAIL" for check in checks) else 0


if __name__ == "__main__":
    sys.exit(main())
