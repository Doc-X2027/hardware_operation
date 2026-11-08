# 硬件系统说明

本仓库存放 AUBO 机械臂、网络相机、USB 相机和三轴力传感器的调用脚本。下表中的地址、通道和版本来自原项目代码及本机已有文件；空白项表示目前没有可核实的信息。表中“已迁入”表示代码和库在仓库中，现场设备是否可用以自检结果为准。

| 硬件 | 型号 | 接口及当前配置 | 必要软件与驱动 | 调用目录 | Windows 适配 | Linux 适配 |
| --- | --- | --- | --- | --- | --- | --- |
| AUBO 机械臂 |  | RPC `192.168.34.10:30004` | AUBO SDK 0.26.0rc6；Python 3.12 绑定 | [aubo_robot](aubo_robot/README.md) | 本机 RPC 端口连接成功；未执行机械臂运动 |  |
| 网络相机 |  | 本机 TCP 服务 `127.0.0.1:8888`；海康 GigE 取流地址 `192.168.34.55` | TCP 服务端程序；GigE 路径需海康 MVS 驱动、仓库内的 `hikrobot` 封装、OpenCV、NumPy | [socket_camera](socket_camera/README.md) | GigE 本机取帧成功；可选 TCP 服务当前未运行 |  |
| USB 相机 |  | OpenCV 设备索引 `0` | OpenCV、NumPy | [usb_camera](usb_camera/README.md) | 本机取帧成功（640×480） |  |
| 三轴力传感器及 ART-DAQ 采集卡 |  | `Dev1/ai0`、`ai1`、`ai2`；1000 Hz；默认 `20 N/V` | ART-DAQ 驱动；仓库含 Python 库、x64 DLL、Python 3.12 编译版传感器模块 | [force_sensor](force_sensor/README.md) | 库可加载；本机 `Dev1` 当前无法访问 | 当前仓库的 ART-DAQ 库仅支持 Windows |

网络相机的 TCP 服务与 GigE 取流代码可能属于同一物理相机的不同调用链；源项目没有足够资料确认它们的设备对应关系。传感器量程、零点条件、相机标定和机械臂安全轨迹也需要按现场设备确认。

当前接线下的自检结果：AUBO RPC `192.168.34.10:30004` 可连接；GigE 相机 `192.168.34.55` 取得 `3072×2048` 图像；USB 索引 `0` 取得 `640×480` 图像。力传感器尚未连接，自检使用 `--skip-force` 跳过。本机 `127.0.0.1:8888` 是旧项目的可选 TCP 相机服务，目前未运行。

## 快速自检

从仓库根目录运行：

```powershell
py -3.12 self_check.py --skip-force
```

脚本检查仓库文件、AUBO RPC 端口、GigE 相机取帧及 USB 相机取帧。力传感器未接入时使用 `--skip-force`；接入后去掉该参数即可读取一次数据。本机 TCP 相机服务是可选检查，需使用 `--check-camera-service` 才会探测其端口。GigE 取帧时会临时关闭触发模式，并在结束后恢复原值。脚本不会让机械臂上电或运动，也不会向 TCP 相机服务发送拍照命令。力传感器检查不做零点校准。默认连接与取帧超时为 5 秒，可用 `--timeout 10` 调整。`PASS` 为检查通过，`FAIL` 为检查失败，`SKIP` 为当前环境或模式未执行。存在 `FAIL` 时退出码为 1。

没有接入设备时可检查文件和脚本自身：

```powershell
py -3.12 self_check.py --offline
py -3.12 self_check.py --offline --json
```

设备地址或索引不同可覆盖默认值，例如：

```powershell
py -3.12 self_check.py --robot-ip 192.168.34.11 --gige-ip 192.168.34.56 --usb-index 1
```

运行完整自检前，需在所用 Python 3.12 环境安装相机和力传感器 Python 依赖，并安装对应硬件驱动：

```powershell
py -3.12 -m pip install -r .\socket_camera\requirements-camera.txt
py -3.12 -m pip install -r .\usb_camera\requirements.txt
py -3.12 -m pip install -r .\force_sensor\requirements.txt
```

Linux 可执行 `python3 self_check.py --offline` 检查目录文件；完整适配情况以表格为准。各硬件的具体控制指令、坐标单位和使用限制见对应目录的说明。
