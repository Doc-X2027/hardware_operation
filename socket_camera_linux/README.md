# Linux GigE 相机取流

使用 **Aravis 0.8 + GTK 3/PyGObject/Cairo + NumPy + OpenCV**，通过 GigE Vision / GenICam 访问相机，不需要 Windows DLL，也不依赖海康 MVS。此目录独立于 `socket_camera/`，默认地址为 `192.168.34.55`。

## 文件

| 文件 | 用途 |
| --- | --- |
| `preview.py` | 与原 socket_camera 一致的画布、缩放和快捷键 |
| `stream.py` | 设备发现、连续采集、窗口预览、单帧保存 |
| `config.json` | IP、每次取帧超时、连续失败上限、缓冲区数量 |
| `run.sh` | 加载本目录中的 Aravis 动态库和 typelib，使用系统 Python |
| `install_local.sh` | 从 Ubuntu 软件源下载并解包 Aravis，无需 sudo |
| `lib/` | 本机运行库、下载包及版权文件；二进制不提交 Git |

## 依赖安装

当前电脑为 Ubuntu 22.04 x86_64，系统 Python 已有 GTK 3、PyGObject/Cairo、NumPy 和 OpenCV。本目录已下载 Aravis 0.8.20-1，可直接使用 `run.sh`。

复制或 Git 克隆到其他 Ubuntu 22.04 电脑后，先运行：

```bash
sudo apt-get install python3-gi python3-gi-cairo gir1.2-gtk-3.0 python3-numpy python3-opencv
bash socket_camera_linux/install_local.sh
```

也可以全部使用系统包：

```bash
sudo apt-get install gir1.2-aravis-0.8 libaravis-0.8-0 python3-gi python3-gi-cairo gir1.2-gtk-3.0 python3-numpy python3-opencv
```

无需 `pip install aravis`。`run.sh` 固定使用 `/usr/bin/python3`，避免虚拟环境无法发现系统 GI 绑定。如果使用系统安装且没有本地库，启动器会自动使用系统搜索路径。

## 运行

从仓库根目录执行：

```bash
# 枚举设备；发现成功不代表可打开或取帧
bash socket_camera_linux/run.sh --list

# 持续预览，Q / Esc 或关闭窗口退出
bash socket_camera_linux/run.sh

# 无窗口采集 100 帧，输出帧数、尺寸和平均 FPS
bash socket_camera_linux/run.sh --headless --frames 100

# 保存一帧并退出
bash socket_camera_linux/run.sh --output socket_camera_linux/captures/frame.png

# 覆盖配置中的相机地址
bash socket_camera_linux/run.sh --ip 192.168.34.55 --headless --frames 10

# 软件模拟验证，不连接真实相机
bash socket_camera_linux/run.sh --simulate --headless --frames 5
```

`--frames 0`（默认）持续取流；Ctrl+C 停止。连续 5 次超时或无效帧后报错退出，默认每次等待 3000 ms，可修改 `config.json`。超时仅作用于接收帧，设备打开使用 Aravis 自身的超时。

支持无行填充的 `Mono8`、四种 `Bayer*8` 及 `RGB8/BGR8`。默认保留原像素格式；遇到不支持的高位深或打包格式，可显式指定相机支持的 `--pixel-format Mono8` 或 `--pixel-format BayerRG8`。脚本不会根据颜色效果猜测 Bayer 排列，使用相机报告的格式转换。

采集期间将当前触发选择器对应的 `TriggerMode` 设置为 `Off`，采集模式设置为 `Continuous`，退出时尝试恢复这两个参数及显式修改的像素格式。不会写入设备持久用户配置；强制终止或断电时无法保证恢复。复杂的多触发选择器配置可能需要在设备管理工具中另行调整。

## 本机验证结果（2026-11-08）

- 已成功加载本目录中的 Aravis 0.8.20；无需管理员安装。
- 模拟相机连续取帧和 PNG 保存通过，尺寸 `512×512`。这仅验证软件流程。
- 真实设备发现返回 `GEV-MV-CU060-10GC-DA7251168`，地址 `192.168.34.55`；随后打开设备核实型号 `MV-CU060-10GC`、序列号 `DA7251168`。
- 初次打开失败；给有线接口应用已有配置中的 `192.168.34.20/24` 后，真实设备成功打开，核实型号 `MV-CU060-10GC`、序列号 `DA7251168`。
- 已真实连续采集 **100 帧**，尺寸 **3072×2048**，格式 **BayerRG8**，采集期间日志约 **14.7 FPS**，命令正常退出，无超时/无效帧日志。
- 已保存真实样张 `captures/verified_frame.png`，PNG 保存成功。样张可见现场物体但明显偏暗；设备当前曝光为 15000 µs、自动曝光关闭、增益为 0。本次保留曝光和增益，图像亮度可后续结合照明调整。
- 修复了 Ubuntu 自带 OpenCV 缺少长名称 Bayer 转换常量的兼容问题；四种 Bayer 排列的合成色块转换均验证通过。
- GTK 原生窗口已连续采集真实图像 30 帧，约 14.4 FPS；通过 GTK 信号注入验证滚轮放大/缩小、平滑滚动和中键复位。未进行人工物理鼠标操作验证；内参尚未标定。

## 网络排查

修复前检测的有线地址为 `192.168.1.10/24`，访问相机的路由走无线网关。GigE 广播发现可以找到设备，但后续单播控制及图像接收仍可能因网段/路由不正确而失败。先检查：

```bash
ip -brief address
ip route get 192.168.34.55
```

应让连接相机的有线网卡具备与相机匹配且无地址冲突的地址及路由。例如相机确认为 `/24` 掩码时，可在系统网络设置中给直连网卡配置一个未占用的 `192.168.34.x/24` 地址。不要把网卡配置为相机自身的 `.55`。取流脚本本身不修改主机或相机网络配置。本次排查已经执行以下命令，将 NetworkManager 连接配置中已有的地址追加到当前接口，保留旧地址及无线连接：

```bash
nmcli device modify enp0s31f6 +ipv4.addresses 192.168.34.20/24
```

修复后 `ip route get 192.168.34.55` 返回 `dev enp0s31f6 src 192.168.34.20`。`device modify` 修改当前活动连接，持久连接配置本身原本已包含 `192.168.34.20/24`；重连后仍应复查路由。若需撤销本次活动地址追加，可执行 `nmcli device modify enp0s31f6 -ipv4.addresses 192.168.34.20/24`，这会中断该路径的相机访问。

同时关闭 Windows MVS、其他采集脚本等可能占用相机控制权的程序，检查防火墙和有线连接。取帧超时但可以打开时，再检查 GigE 数据包大小、网卡 MTU 和流量丢包；发现列表为空时先检查网线、供电、网段和接口。

取流库不保证设备有出厂内参；内参仍需设备专属标定文件或标定板实拍计算。

## 预览窗口交互

与 `socket_camera/hikrobot_stream.py` 一致：初始窗口 1200×800，可调整大小；图像保持比例居中显示，空白区域为深色，放大后超出窗口部分裁剪。鼠标滚轮按 1.15 倍步进缩放（0.05～50 倍相对于适配窗口的比例），中键恢复适配窗口；按 S 保存完整分辨率的当前帧到工作目录 `camera_<IP>.jpg`，不会保存缩放画布；Q / Esc 或关闭窗口退出。再次按 S 会覆盖同名文件。


滚轮事件由 GTK 3 原生窗口处理，支持普通滚轮和触控板平滑滚动，标题中的 `Zoom` 实时显示缩放倍数。这里不再使用 OpenCV HighGUI 的滚轮回调；本机 GTK 后端无法按 Windows 的方式可靠接收该事件（参见 [OpenCV HighGUI 文档](https://docs.opencv.org/4.13.0/d7/dfc/group__highgui.html)）。当前主机已具备 GTK/PyGObject/Cairo 依赖。

代码更新后，关闭旧窗口及旧取流进程，再执行 `bash socket_camera_linux/run.sh`。将鼠标移到图像区域，上滚放大、下滚缩小；标题中的 `Zoom` 应随操作变化。触控板平滑滚动按滚动量连续调整倍率。窗口预览需要图形桌面；SSH 等无图形会话使用 `--headless` 或 `--output`。


## 上游资料

- [Aravis 官方 Python 示例](https://github.com/AravisProject/aravis/blob/main/tests/python/arv-camera-test.py)
- [Aravis 0.8 Camera API](https://aravisproject.github.io/aravis/aravis-stable/class.Camera.html)
- [Aravis 项目及许可](https://github.com/AravisProject/aravis)
