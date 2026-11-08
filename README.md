# 硬件系统说明

本仓库存放 AUBO 机械臂、网络相机、USB 相机和三轴力传感器的调用脚本。下表中的地址、通道和版本来自原项目代码及本机已有文件；未确认项表示目前没有可核实的信息，不根据 IP 地址或图像尺寸推测设备型号。检测结果仅代表记录时的环境；历史记录与最新 Linux 取流结果分别注明。

| 硬件 | 型号 | 接口及当前配置 | 必要软件与驱动 | 调用目录 | Windows 适配 | Linux 适配 |
| --- | --- | --- | --- | --- | --- | --- |
| AUBO 机械臂 | 未确认 | RPC `192.168.34.10:30004` | AUBO SDK 0.26.0rc6；Python 3.12 绑定 | [aubo_robot](aubo_robot/README.md) | 历史记录：RPC 端口连接成功；未执行运动 | 初次 RPC 超时，网络修复后未复测；仓库绑定为 Windows `.pyd`，控制功能需另配 Linux SDK |
| 网络相机 | `MV-CU060-10GC`，SN `DA7251168` | GigE `192.168.34.55`；可选旧 TCP 服务 `127.0.0.1:8888` | Windows：MVS；Linux：Aravis 0.8、GTK 3/PyGObject/Cairo、OpenCV、NumPy | [Windows/MVS](socket_camera/README.md)、[Linux/Aravis](socket_camera_linux/README.md) | 历史记录：GigE 取帧成功；可选 TCP 服务未运行 | 真实取流通过：3072×2048，约 14.7 FPS；GTK 预览通过 |
| USB 相机 | 系统标识见本次自检记录 | 本机内置索引 `0`、外接索引 `4` | OpenCV、NumPy | [usb_camera](usb_camera/README.md) | 历史记录：取帧成功（640×480） | 本次索引 0、4 均取帧成功，详见下表 |
| 三轴力传感器及 ART-DAQ 采集卡 | 传感器及采集卡型号均未确认 | `Dev1/ai0`、`ai1`、`ai2`；1000 Hz；默认 `20 N/V` | ART-DAQ 驱动；仓库含 Python 库、x64 DLL、Python 3.12 编译版传感器模块 | [force_sensor](force_sensor/README.md) | 历史记录：库可加载，`Dev1` 无法访问 | 当前仓库的 ART-DAQ 库仅支持 Windows |

网络相机的 TCP 服务与 GigE 取流代码可能属于同一物理相机的不同调用链；源项目没有足够资料确认它们的设备对应关系。传感器量程、零点条件、相机标定和机械臂安全轨迹也需要按现场设备确认。

> 最新状态：Linux Aravis 路径已实现真实取流，见文末“Linux 独立取流入口”。下方初次检测中的 MVS 加载失败属于原 `self_check.py` 路径，不代表新取流脚本失败。

## 初次硬件自检（2026-11-08，北京时间）

运行环境为 Linux x86_64、Python 3.10.12。在仓库根目录执行 `python3 self_check.py --check-camera-service --json`，退出码为 **1**，结果如下。此前 Windows 的连接和取帧记录只作为历史参考，不代表当前机器的状态。

| 检查项 | 结果 | 实测详情 |
| --- | --- | --- |
| 仓库文件 | PASS | 脚本列出的 8 个必需文件齐全；不代表所有实验脚本的依赖齐全 |
| 运行环境 | PASS | 脚本可运行；该项仅报告平台与 Python 版本，不代表所有 SDK 兼容 |
| AUBO RPC | FAIL | `192.168.34.10:30004` 连接超时；路由选择本机地址 `10.63.17.221` |
| TCP 相机服务（可选） | FAIL | `127.0.0.1:8888` 拒绝连接 |
| GigE 相机 | FAIL | 加载 SDK 时出现 `NoneType + str`；`MVCAM_COMMON_RUNENV` 未设置，常见安装目录 `/opt/MVS` 不存在，尚未进入设备发现及取帧阶段 |
| USB 相机，索引 0 | PASS | 成功取帧 `1920×1080`；系统标识为 `Integrated_Webcam_FHD`，是内置摄像头 |
| 力传感器 | SKIP | 当前模块要求 Windows x64 / Python 3.12；本次未读取力数据，不能据此判断设备连接状态 |

补充调用 `self_check.usb_probe(4)`，外接相机索引 **4**（系统标识 `icspring camera`）成功取得 **640×480** 图像。系统当前存在 `/dev/video0` 至 `/dev/video5`；视频节点数量不等于物理相机数量，索引也可能随插拔变化。OpenCV 输出了 GStreamer 警告，但这两次读取均返回有效图像。

离线检查 `python3 self_check.py --offline --json` 退出码为 **0**，硬件项全部跳过。本次没有执行机械臂上电、启动或运动，没有进行力传感器零点校准。

## 目录与入口

| 路径 | 用途 |
| --- | --- |
| `self_check.py` | 文件、网络端口、相机单帧及力传感器读数检查 |
| `aubo_robot/control.py` | 机械臂状态及控制命令；使用前阅读对应目录说明 |
| `socket_camera/hikrobot_stream.py` | 海康 GigE 预览、参数查询和图像保存 |
| `socket_camera_linux/run.sh` | Linux Aravis 取流入口，支持 GTK 预览、无窗口采集和保存 |
| `socket_camera/hikvision.py` | 旧项目 TCP 相机服务客户端；仓库未包含服务端 |
| `usb_camera/control.py` | USB 拍照及颜色识别 |
| `force_sensor/control.py` | 三轴力单次、平均及连续读取 |

原始集成/力控实验脚本仍有缺失依赖，详见各目录 README。USB 识别坐标为像素坐标，不能直接作为机械臂坐标；力传感器适配器补齐的三个力矩分量为零，不是真实六维测量。

## 快速自检

从仓库根目录运行：

```powershell
py -3.12 self_check.py --skip-force
```

脚本检查仓库文件、AUBO RPC 端口、GigE 相机取帧及 USB 相机取帧。力传感器未接入时使用 `--skip-force`；接入后去掉该参数即可读取一次数据。本机 TCP 相机服务是可选检查，需使用 `--check-camera-service` 才会探测其端口。GigE 取帧时会临时关闭触发模式，并在结束后恢复原值。脚本不会让机械臂上电或运动，也不会向 TCP 相机服务发送拍照命令。力传感器检查不做零点校准。TCP 连接、GigE 单帧等待及力采集子进程默认超时为 5 秒，可用 `--timeout 10` 调整；该参数不限制 USB 取帧或整个自检过程。`PASS` 为检查通过，`FAIL` 为检查失败，`SKIP` 为当前环境或模式未执行。存在 `FAIL` 时退出码为 1。

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

Linux 使用 `python3` 运行；本机已具备 USB 取帧所需依赖。检查本次发现的外接 USB 相机：

```bash
python3 self_check.py --usb-index 4 --check-camera-service
```

该命令仍会检查机械臂和 GigE 相机；当前力传感器会因平台限制自动跳过。Windows `.pyd`、DLL 及现有力传感器加载器不能直接在 Linux 使用。

## 自检参数

| 参数 | 默认值 | 说明 |
| --- | --- | --- |
| `--offline` | 关闭 | 仅检查必需文件并报告运行环境 |
| `--skip-force` | 关闭 | 主动跳过力传感器读取 |
| `--check-camera-service` | 关闭 | 检查可选 TCP 服务端口，不发送拍照命令 |
| `--json` | 关闭 | 以 JSON 输出检查结果；库的诊断日志可能另行输出 |
| `--robot-ip` / `--robot-port` | `192.168.34.10` / `30004` | 机械臂 RPC 目标 |
| `--socket-host` / `--socket-port` | `127.0.0.1` / `8888` | TCP 相机服务目标 |
| `--gige-ip` | `192.168.34.55` | GigE 相机目标 |
| `--usb-index` | `0` | OpenCV 设备索引，需大于或等于 0 |
| `--timeout` | `5.0` 秒 | TCP、GigE 单帧和力采集等待时间，必须大于 0 |

`PASS` 仅表示对应检查通过：RPC 端口可连接不等于 SDK 登录、机械臂状态或运动能力已验证；单帧成功不等于完成标定或长期稳定性验证。全部通过或仅有跳过项时退出码为 0，参数错误退出码为 2。

## 本次故障排查与复检

1. **网络状态**：初次检测时访问相机走无线网卡；现已给有线接口 `enp0s31f6` 应用 `192.168.34.20/24`，相机流量通过有线接口直连。相机真实取流已通过，机械臂 RPC 尚未在网络修复后复测，不能据此认定机械臂可用。重连后用 `ip route get 192.168.34.55` 核对路由。
2. **GigE 取流路径**：本机 Linux 使用 `socket_camera_linux/run.sh`，无需 MVS。`self_check.py` 仍使用原 MVS 封装，未接入 Aravis；该脚本的 SDK 加载失败不代表 Linux 新取流脚本失败。若使用原 MVS 路径，则仍需安装对应 SDK 并配置 `MVCAM_COMMON_RUNENV`。
3. **TCP 服务**：只有使用旧项目 TCP 调用链时才需要启动服务端；本仓库仅含客户端。若只使用 GigE 直连，可不加 `--check-camera-service`。
4. **USB 相机选择**：当前默认索引 0 是内置摄像头，外接 `icspring camera` 使用索引 4。应用中通过 `--index 4` 指定，自检中通过 `--usb-index 4` 指定；重新插拔后核对索引。
5. **力传感器**：在 Windows x64 / Python 3.12 下安装 ART-DAQ 驱动和 Python 依赖，确认设备管理工具中存在 `Dev1` 及三路输入，再去掉 `--skip-force` 复检。当前 Linux 环境需要另行适配驱动及传感器实现。

各硬件的具体控制指令、坐标单位和使用限制见对应目录的说明。未确认的机械臂、相机、传感器和采集卡具体型号，需根据设备铭牌或厂商设备管理工具补录。


## 相机内参与标定记录

2026-11-08 已检索本仓库标定相关代码和常见标定文件，并查询公开资料、读取外接 USB 相机的 USB 描述符和 V4L2 控制项。目前**两台目标相机都没有取得可验证的内参**。下表中的“待标定”不能替换为零或其他同型号相机的参数，也不能直接用于测距或机械臂定位。

| 项目 | 外接 USB 相机 | 海康 GigE 相机 |
| --- | --- | --- |
| 设备身份 | `icSpring / icspring camera`，USB VID:PID `2993:0858` | Aravis 已读取型号 `MV-CU060-10GC`；镜头型号未确认 |
| 序列号 | USB 描述符报告 `20240307110322` | `DA7251168` |
| 连接位置 | 本次 `/dev/video4`，OpenCV 索引 `4` | 配置 IP `192.168.34.55` |
| 图像尺寸 | 本次实测 `640×480` | Linux Aravis 实测 `3072×2048` |
| 像素焦距 `fx, fy` | 待标定 | 待标定或读取设备专属标定数据 |
| 主点 `cx, cy` | 待标定 | 待标定或读取设备专属标定数据 |
| 畸变模型、畸变系数 | 待标定 | 待标定或读取设备专属标定数据 |
| 重投影 RMS 误差（像素） | 未标定 | 未标定 |
| 标定文件及标定日期 | 暂无 | 暂无 |

Linux 已通过 Aravis 读取相机型号、序列号并完成实际取流，但尚未获得内参或畸变系数。分辨率和取流成功不能代替标定。

### 已尝试的读取方式与结论

- **仓库搜索**：未找到可用的相机矩阵或畸变系数文件；`usb_camera/shijue.py` 中的 `calibrate()` 只是返回输入坐标，不执行相机标定。
- **USB 直接读取**：`lsusb -v -d 2993:0858` 可读取上述身份信息。描述符的 `wObjectiveFocalLengthMin`、`wObjectiveFocalLengthMax`、`wOcularFocalLength` 均为 0，未提供可用焦距信息；不能将这些 0 写成 `fx/fy`。通过 `VIDIOC_QUERYCTRL` 枚举到曝光、增益、亮度、白平衡等控制项，未发现相机矩阵或畸变系数控制项。这仅说明当前公开接口没有暴露内参，不排除厂商私有接口或独立标定文件。
- **公开资料查询**：按 `icspring`、USB ID `2993:0858` 和内参关键词检索，未找到可核实且匹配该设备与分辨率的厂商标定数据。海康型号现已读取为 `MV-CU060-10GC`，镜头及设备专属标定文件尚未确认，不能套用网络参数。
- **GigE 内参状态**：Aravis 已完成设备打开和取流；尚未完成标定参数节点或设备专属标定文件检查，因此不能判断设备是否保存了出厂内参。

### 获得真实内参的方法

若厂商能提供与设备序列号、镜头和当前图像模式匹配的出厂标定文件，可记录其矩阵、畸变模型和适用条件。否则应分别对两台相机进行实物标定：

1. 准备平整的棋盘格或 ChArUco 标定板，确认内角点数量及实际格子尺寸。
2. 固定实际使用的镜头、焦距/对焦、分辨率和 ROI；两台相机分别采集标定图片，包含不同距离、倾角及画面边缘位置，避免所有图片只有同一姿态。
3. 使用匹配镜头的模型标定。例如普通针孔模型可通过 OpenCV `calibrateCamera` 求解相机矩阵和畸变参数；鱼眼镜头应选用对应模型。
4. 保存原始图片和标定文件，记录设备序列号、镜头/对焦条件、图像尺寸、ROI、有效图片数量、标定日期及重投影误差，并用额外图片检查去畸变效果。
5. 将验证后的数值填入上表。更换镜头、改变对焦或裁剪模式后需重新评估标定适用性；不能只修改分辨率标签继续沿用原值。

普通 OpenCV 针孔模型的记录格式为：

```text
K = [[fx,  0, cx],
     [ 0, fy, cy],
     [ 0,  0,  1]]
D = [k1, k2, p1, p2, k3]  # 仅适用于使用该五参数模型的标定结果
```

其中 `fx, fy, cx, cy` 的单位为像素，畸变系数无量纲；这些符号是字段说明，不是已测得的数值。内参标定也不能替代相机与机械臂之间的外参/手眼标定。

资料来源：[OpenCV 相机标定教程](https://docs.opencv.org/4.5.4/d4/d94/tutorial_camera_calibration.html)、[OpenCV 标定 API](https://docs.opencv.org/4.12.0/d9/d0c/group__calib3d.html)、[海康机器人官方下载中心](https://www.hikrobotics.com/en/machinevision/service/download/?module=0)。这些来源说明标定方法或 SDK 获取渠道，不提供本机两台相机的实测内参。


## Linux 独立取流入口

当前电脑使用 [socket_camera_linux](socket_camera_linux/README.md)，默认相机为 `192.168.34.55`，无需海康 MVS。请在仓库根目录执行：

```bash
# 实时窗口预览
bash socket_camera_linux/run.sh

# 无窗口采集 100 帧后退出
bash socket_camera_linux/run.sh --headless --frames 100

# 保存一帧
bash socket_camera_linux/run.sh --output socket_camera_linux/captures/frame.png
```

窗口初始尺寸为 **1200×800**，图像等比例居中显示。**上滚放大、下滚缩小、中键复位**，标题 `Zoom` 显示当前倍数；`S` 保存完整分辨率图片至当前工作目录 `camera_<IP>.jpg`，`Q` / `Esc` 或关闭窗口退出。窗口使用 GTK 原生滚轮事件，支持触控板平滑滚动。代码更新后需关闭旧进程再重新启动。

2026-11-08 验证结果：真实相机连续采集 100 帧，3072×2048、BayerRG8，约 14.7 FPS；GTK 窗口连续取流 30 帧，约 14.4 FPS；GTK 信号注入验证上滚、下滚、平滑滚动及中键复位。上述帧率为本次测试值，不是性能保证。真实样张保存在 `socket_camera_linux/captures/verified_frame.png`（本机文件，未提交 Git）；画面偏暗，曝光和增益保留原值，内参尚未标定。

安装依赖、本地库下载、配置参数及网络排查见 [Linux 取流说明](socket_camera_linux/README.md)。
