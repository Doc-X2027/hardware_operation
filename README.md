> 2026-11-10 外接 USB 相机已重新确认：`icspring camera`，VID:PID `2993:0858`，序列号 `20240307110322`，当前 `/dev/video4`。默认按身份选择，不再使用内置索引 0；下方旧记录中索引 0 的 PASS 仅表示内置相机返回了数据，不能证明外接相机可用。

# 硬件系统说明

本仓库存放 AUBO 机械臂、网络相机、USB 相机和三轴力传感器的调用脚本。下表中的地址、通道和版本来自原项目代码及本机已有文件；未确认项表示目前没有可核实的信息，不根据 IP 地址或图像尺寸推测设备型号。检测结果仅代表记录时的环境；历史记录与最新 Linux 取流结果分别注明。

| 硬件 | 型号 | 接口及当前配置 | 必要软件与驱动 | 调用目录 | Windows 适配 | Linux 适配 |
| --- | --- | --- | --- | --- | --- | --- |
| AUBO 机械臂 | 未确认 | RPC `192.168.34.10:30004` | AUBO SDK 0.26.0rc6；Python 3.12 绑定 | [aubo_robot](aubo_robot/README.md) | 历史记录：RPC 端口连接成功；未执行运动 | 2026-11-09 RPC 超时；仓库绑定为 Windows `.pyd`，控制功能需另配 Linux SDK |
| 网络相机 | `MV-CU060-10GC`，SN `DA7251168` | GigE `192.168.34.55`；可选旧 TCP 服务 `127.0.0.1:8888` | Windows：MVS；Linux：Aravis 0.8、GTK 3/PyGObject/Cairo、OpenCV、NumPy | [Windows/MVS](socket_camera/README.md)、[Linux/Aravis](socket_camera_linux/README.md) | 历史记录：GigE 取帧成功；可选 TCP 服务未运行 | 历史真实取流通过；2026-11-09 Aravis 依赖通过，设备无法连接 |
| USB 相机 | 系统标识见本次自检记录 | 本机内置索引 `0`、外接索引 `4` | OpenCV、NumPy；Linux 预览另需 GTK 3/PyGObject/Cairo | [Windows](usb_camera/README.md)、[Linux](usb_camera_linux/README.md) | 历史记录：取帧成功（640×480） | 2026-11-09 索引 0 取帧成功；索引 4 为历史记录 |
| 三轴力传感器及 ART-DAQ 采集卡 | 传感器及采集卡型号均未确认 | `Dev1/ai0`、`ai1`、`ai2`；1000 Hz；默认 `20 N/V` | ART-DAQ 驱动；仓库含 Python 库、x64 DLL、Python 3.12 编译版传感器模块 | [force_sensor](force_sensor/README.md) | 历史记录：库可加载，`Dev1` 无法访问 | 当前仓库的 ART-DAQ 库仅支持 Windows |

网络相机的 TCP 服务与 GigE 取流代码可能属于同一物理相机的不同调用链；源项目没有足够资料确认它们的设备对应关系。传感器量程、零点条件、相机标定和机械臂安全轨迹也需要按现场设备确认。

> 自检已按平台选择 GigE 后端：Windows 使用 MVS，Linux 使用 Aravis。2026-11-09 复检结果见下文；历史检测结果不代表设备当前在线。

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
| `usb_camera/control.py` | Windows USB 拍照、持续取流及滚轮缩放 |
| `usb_camera_linux/control.py` | Linux USB 拍照、GTK 取流及滚轮缩放 |
| `force_sensor/control.py` | 三轴力单次、平均及连续读取 |

原始集成/力控实验脚本仍有缺失依赖，详见各目录 README。力传感器适配器补齐的三个力矩分量为零，不是真实六维测量。

## 快速自检

Linux 使用系统 Python；Aravis 检查自动加载 `socket_camera_linux/lib` 中的本地库，未安装本地库时使用系统库：

```bash
# 离线检查入口文件和相机依赖，不连接硬件
/usr/bin/python3 self_check.py --offline

# 检查设备，力传感器在 Linux 自动跳过
/usr/bin/python3 self_check.py

# 只检查 USB，相机索引按实际设备选择
/usr/bin/python3 self_check.py --skip-robot --skip-gige --skip-force

# 多台 USB 相机、图形环境检查、JSON 输出
/usr/bin/python3 self_check.py --skip-robot --skip-gige --skip-force --check-preview --json
```

索引 `4` 是此前外接相机的记录，不保证当前存在；可先查看 `ls /dev/video*`，视频节点数量不等于物理相机数量。Linux 依赖安装参见 [GigE](socket_camera_linux/README.md) 和 [USB](usb_camera_linux/README.md)。

Windows 在 PowerShell 中使用 x64 Python 3.12，以匹配仓库的 AUBO 和力传感器二进制：

```powershell
py -3.12 -m pip install -r .\socket_camera\requirements-camera.txt
py -3.12 -m pip install -r .\usb_camera\requirements.txt
py -3.12 -m pip install -r .\force_sensor\requirements.txt
py -3.12 self_check.py --offline
py -3.12 self_check.py --skip-force --usb-index 1
```

Windows GigE 需要安装 MVS，力传感器需要 ART-DAQ 驱动及 `Dev1`；pip 依赖不能替代设备驱动。力传感器接入后去掉 `--skip-force`，读取一次三轴数据，不做零点校准。

默认检查仓库入口文件、运行环境、相机依赖、AUBO RPC 端口、GigE 单帧、USB 单帧及力传感器读数。`--skip-gige`、`--skip-usb` 同时跳过该相机的依赖检查；文件完整性始终检查。Linux 不要求 Windows 专属 `.pyd`、DLL 或 `.pyc` 存在；Windows 会额外检查这些文件。SDK 平台匹配不代表 SDK 导入、登录或驱动访问已验证。

自检不会让机械臂上电或运动，不向旧 TCP 相机服务发送拍照命令，不修改主机网络配置。GigE 取帧会临时关闭触发模式，Aravis 还会临时设置连续采集模式；正常退出尝试恢复。超时强制终止时无法保证恢复，重新采集前应核对相机模式。

## 自检参数与结果

| 参数 | 默认值 | 说明 |
| --- | --- | --- |
| `--offline` | 关闭 | 检查入口文件和依赖，跳过所有硬件连接 |
| `--skip-robot` | 关闭 | 跳过机械臂 RPC 端口 |
| `--skip-gige` | 关闭 | 跳过 GigE 依赖和取帧 |
| `--skip-usb` | 关闭 | 跳过 USB 依赖和取帧 |
| `--skip-force` | 关闭 | 跳过力传感器读取 |
| `--check-preview` | 关闭 | 检查 GTK/显示服务或创建 Windows OpenCV 测试窗口；不验证鼠标操作 |
| `--check-camera-service` | 关闭 | 检查可选 TCP 服务端口，不发送拍照命令 |
| `--json` | 关闭 | 标准输出为 JSON 数组；SDK 日志被子进程捕获 |
| `--robot-ip` / `--robot-port` | `192.168.34.10` / `30004` | 机械臂 RPC 目标 |
| `--socket-host` / `--socket-port` | `127.0.0.1` / `8888` | 旧 TCP 相机服务目标 |
| `--gige-ip` | `192.168.34.55` | GigE 相机目标 |
| `--gige-backend` | `auto` | Linux 自动使用 `aravis`，其他平台使用 `mvs`；可显式指定 |
| `--usb-index` | 未指定 | Linux 按 `usb_camera_linux/config.json` 匹配外接相机；Windows 必须明确指定索引。Linux 显式索引也必须匹配目标身份 |
| `--timeout` | `5.0` 秒 | 每项 TCP 连接或检查子进程的超时上限，必须为有限正数 |

检查按顺序执行，`--timeout` 不是整个自检的总时长。USB、MVS、Aravis 和依赖检查运行在独立子进程中，超时或原生库崩溃记为 FAIL 后继续其他项目。Aravis 子进程固定使用 `/usr/bin/python3`，加载其配置文件中的帧等待/重试设置；外层 `--timeout` 限制整个子进程。其他检查使用启动自检的 Python，推荐 Linux 全程使用系统 Python。DNS 解析可能受操作系统解析器超时影响，现场地址推荐直接使用 IP。

`--offline --check-preview` 仍会检查图形环境，但不连接相机。SSH/无图形桌面下不要指定 `--check-preview`，拍摄和无窗口取流不需要显示服务。仅检查文件与运行环境可使用 `--offline --skip-usb --skip-gige`。

| 状态/退出码 | 含义 |
| --- | --- |
| PASS | 对应检查通过；端口连通不等于 SDK 登录成功，单帧成功不等于长期取流稳定或已标定 |
| FAIL | 文件、依赖、连接或读取失败，或检查超时/崩溃 |
| SKIP | 主动跳过、平台不支持、离线模式，或前置依赖失败后跳过设备；不表示硬件可用 |
| 退出码 0 | 没有 FAIL，可能包含 SKIP |
| 退出码 1 | 至少一个 FAIL |
| 退出码 2 | 命令行参数错误 |

JSON 保留数组结构，每项包含 `item`、`status`、`detail`；USB 项名称带索引。例如：

```json
[{"item": "USB 相机 [0]", "status": "PASS", "detail": "设备索引 0，图像 1920x1080"}]
```

## 最新复检（2026-11-09，北京时间）

执行 `/usr/bin/python3 self_check.py --skip-force --check-preview --timeout 10 --json`，退出码 **1**：

| 检查项 | 结果 | 详情 |
| --- | --- | --- |
| 仓库文件、运行环境 | PASS | Linux x64，系统 Python 3.10.12 |
| USB 依赖 | PASS | OpenCV 4.5.4、NumPy 1.21.5 |
| GigE 依赖 | PASS | Aravis 0.8、GI、OpenCV、NumPy 可加载 |
| 预览环境 | PASS | GTK/Cairo 可加载，显示服务可连接；本次未验证鼠标事件 |
| AUBO RPC | FAIL | `192.168.34.10:30004` 超时，本机路由源地址为 `10.42.30.90` |
| GigE 相机 | FAIL | Aravis 无法连接 `192.168.34.55`，未进入取帧阶段 |
| USB 相机 [0] | PASS | 单帧 `1920×1080` |
| Windows SDK 平台、TCP 服务、力传感器 | SKIP | 平台不匹配、未启用可选端口检查、显式跳过力采集 |

离线自检通过。无硬件回归测试覆盖日志隔离、子进程崩溃/超时、相机参数恢复失败、离线不访问硬件、多 USB 索引去重及非法参数：

```bash
/usr/bin/python3 -m unittest discover -s tests -v
```

Windows 分支尚未实机验证；本次未检查外接索引 4，也未读取力数据。上方 2026-11-08 的设备成功记录保留供历史对照。

## 故障排查

1. **依赖失败**：先根据对应目录 README 安装依赖。Linux GI 推荐系统 Python；本地 Aravis 库缺失时运行 `bash socket_camera_linux/install_local.sh` 或安装系统包。
2. **网络设备无法连接**：先检查供电、网线及 `ip route get 192.168.34.55`、`ip route get 192.168.34.10`；确认直连网卡具有正确网段和路由。此前的网络修复不保证当前会话仍生效，自检不会自动更改网络。
3. **设备可发现但取帧失败**：关闭占用相机的 MVS/取流进程，检查触发模式、包大小与防火墙；必要时使用 `--timeout 15`。发现、打开与成功取帧是不同阶段。
4. **USB 无法打开**：核对索引、设备权限及占用；应用入口使用 `--index`，自检使用 `--usb-index`。Linux 预览使用 `usb_camera_linux/`，Windows 使用 `usb_camera/`。
5. **力传感器失败**：在 Windows x64 / Python 3.12 环境确认 ART-DAQ 驱动、`Dev1` 和三路输入。Linux 平台跳过不代表设备正常。
6. **TCP 服务失败**：仅旧 TCP 调用链需要该服务，本仓库只有客户端；GigE 直连不需要 `--check-camera-service`。

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

- **仓库搜索**：未找到可用的相机矩阵或畸变系数文件。
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

## 当前外接 USB 相机指令

从仓库根目录执行，Linux 自动匹配 `usb_camera_linux/config.json` 中的设备身份：

```bash
/usr/bin/python3 usb_camera_linux/control.py stream
/usr/bin/python3 usb_camera_linux/control.py capture --output usb_camera_linux/captures/external.png
/usr/bin/python3 self_check.py --skip-robot --skip-gige --skip-force --timeout 10
```

2026-11-10 实拍确认画面含物体轮廓，640×480，偏暗但非全黑；默认入口连续采集 30 帧成功，约 16.6 FPS。10 项回归测试通过，显式索引 0 被身份校验拒绝。设备缺失时直接失败，不自动回退内置相机。自检会丢弃启动帧并报告灰度统计；接近全黑或缺少灰度变化记为 FAIL，需排查遮挡/照明/曝光，不据此推断设备身份。Windows 需现场确认索引并显式使用 `--index` / `--usb-index`，Linux 索引 4 不可直接套用。
