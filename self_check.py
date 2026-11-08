"""Hardware checks without robot power or motion commands."""

import argparse
from ctypes import POINTER, cast
import json
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
        return result("GigE 相机", "FAIL", f"SDK 发现设备失败: {exc}")


def usb_probe(index):
    try:
        import cv2

        cap = cv2.VideoCapture(index)
        try:
            if not cap.isOpened():
                return result("USB 相机", "FAIL", f"设备索引 {index} 无法打开")
            ok, frame = cap.read()
            if not ok or frame is None:
                return result("USB 相机", "FAIL", f"设备索引 {index} 无法取帧")
            return result("USB 相机", "PASS", f"设备索引 {index}，图像 {frame.shape[1]}x{frame.shape[0]}")
        finally:
            cap.release()
    except Exception as exc:
        return result("USB 相机", "FAIL", f"取帧失败: {exc}")


def force_probe(timeout):
    if os.name != "nt" or sys.version_info[:2] != (3, 12):
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
    except (ValueError, IndexError) as exc:
        return result("力传感器", "FAIL", f"读数格式异常: {exc}")


def main():
    parser = argparse.ArgumentParser(description="硬件自检；不触发 TCP 拍照服务、不控制机械臂运动")
    parser.add_argument("--offline", action="store_true", help="只检查文件与运行环境")
    parser.add_argument("--skip-force", action="store_true", help="力传感器未连接时跳过读数")
    parser.add_argument("--check-camera-service", action="store_true", help="额外检查本机 TCP 相机服务端口")
    parser.add_argument("--json", action="store_true", help="输出 JSON")
    parser.add_argument("--robot-ip", default="192.168.34.10")
    parser.add_argument("--robot-port", type=int, default=30004)
    parser.add_argument("--socket-host", default="127.0.0.1")
    parser.add_argument("--socket-port", type=int, default=8888)
    parser.add_argument("--gige-ip", default="192.168.34.55")
    parser.add_argument("--usb-index", type=int, default=0)
    parser.add_argument("--timeout", type=float, default=5.0, help="网络与力采集超时，秒")
    args = parser.parse_args()
    if args.timeout <= 0 or args.usb_index < 0:
        parser.error("--timeout 必须大于 0；--usb-index 必须大于或等于 0")

    checks = []
    required = (
        "aubo_robot/control.py", "aubo_robot/pyaubo_sdk.cp312-win_amd64.pyd",
        "socket_camera/hikvision.py", "socket_camera/hikrobot_stream.py",
        "usb_camera/control.py", "force_sensor/force_sensor.py",
        "force_sensor/legacy/force_sensor.cpython-312.pyc",
        "force_sensor/native/Art_DAQ.dll",
    )
    missing = [path for path in required if not (ROOT / path).is_file()]
    checks.append(result("仓库文件", "FAIL" if missing else "PASS", missing or "必需文件齐全"))
    checks.append(result("运行环境", "PASS", f"{sys.platform}, Python {sys.version.split()[0]}"))

    if args.offline:
        for name in ("AUBO RPC", "TCP 相机服务", "GigE 相机", "USB 相机", "力传感器"):
            checks.append(result(name, "SKIP", "离线模式"))
    else:
        checks.append(tcp_probe("AUBO RPC", args.robot_ip, args.robot_port, args.timeout))
        checks.append(
            tcp_probe("TCP 相机服务", args.socket_host, args.socket_port, args.timeout)
            if args.check_camera_service
            else result("TCP 相机服务", "SKIP", "可选服务；使用 --check-camera-service 检查")
        )
        checks.append(gige_probe(args.gige_ip, args.timeout))
        checks.append(usb_probe(args.usb_index))
        checks.append(
            result("力传感器", "SKIP", "尚未连接；由 --skip-force 跳过")
            if args.skip_force else force_probe(args.timeout)
        )

    if args.json:
        print(json.dumps(checks, ensure_ascii=False, indent=2))
    else:
        for check in checks:
            print(f"[{check['status']}] {check['item']}: {check['detail']}")
    return 1 if any(check["status"] == "FAIL" for check in checks) else 0


if __name__ == "__main__":
    sys.exit(main())
