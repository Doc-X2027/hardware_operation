# Linux USB 相机拍摄与取流

使用 OpenCV 读取 USB 摄像头，`control.py` 仅提供 `capture`（拍摄）和 `stream`（连续取流）两个指令。Linux 默认按 `config.json` 中的 VID/PID 和序列号匹配外接相机，不再默认打开索引 0。

## 安装依赖

Ubuntu/Linux 预览使用与 `socket_camera_linux` 相同的 GTK 3 原生窗口，支持鼠标滚轮和触控板平滑滚动：

```bash
sudo apt-get install python3-gi python3-gi-cairo gir1.2-gtk-3.0 python3-numpy python3-opencv
```

以下命令从仓库根目录执行，使用系统 Python，确保能加载 GI 绑定。USB 相机不需要 Aravis、MVS 或网络配置。

## 拍摄和取流

```bash
# 拍摄一帧，自动创建输出目录
/usr/bin/python3 usb_camera_linux/control.py capture --output usb_camera_linux/captures/frame.png

# 持续取流并打开预览窗口
/usr/bin/python3 usb_camera_linux/control.py stream

# 选择外接 USB 相机
/usr/bin/python3 usb_camera_linux/control.py --index 4 stream

# 无窗口采集 100 帧，输出尺寸及平均 FPS
/usr/bin/python3 usb_camera_linux/control.py stream --headless --frames 100

# 修改连续读取失败上限
/usr/bin/python3 usb_camera_linux/control.py stream --max-failures 5
```

`--frames 0`（默认）持续取流，Ctrl+C 停止。连续读取失败默认达到 5 次后报错退出，成功读取一帧即重置失败计数。USB 使用 OpenCV 后端及相机默认分辨率、帧率；GigE 的 IP、接收超时和 Aravis 缓冲区配置不适用于这里。`cap.read()` 的阻塞时长由设备驱动和 OpenCV 后端决定，失败次数不表示超时时间。

## 预览窗口交互

取流窗口配置参考 `socket_camera_linux/preview.py`：

- 初始窗口 1200×800，可调整大小；图像保持比例居中，背景为深色。
- 鼠标上滚放大、下滚缩小，每步 1.15 倍；支持触控板平滑滚动。
- 缩放范围为适配窗口比例的 0.05～50 倍，超出窗口部分裁剪；标题显示当前倍率。
- 鼠标中键恢复适配窗口。
- S 保存完整分辨率的当前帧到工作目录 `usb_camera_video<索引>.jpg`，再次按 S 覆盖同名文件。
- Q / Esc 或关闭窗口退出。

预览需要图形桌面和 GTK 依赖；无图形会话使用 `capture` 或 `stream --headless`。

Windows 版本见 [usb_camera](../usb_camera/README.md)。两个目录可独立运行。

## 自检

从仓库根目录执行，检查 USB 依赖及单帧读取：

```bash
/usr/bin/python3 self_check.py --skip-robot --skip-gige --skip-force
```

默认自检匹配配置目标；可用 `--usb-index 4` 明确指定当前节点，但仍校验身份。添加 `--check-preview` 检查窗口环境，添加 `--offline` 仅检查文件和依赖。自检不保存图片，默认每项超时 5 秒，详见 [根目录自检说明](../README.md#自检参数与结果)。

## 外接相机身份与画面检查（2026-11-10）

目标为 `icSpring / icspring camera`，USB VID:PID `2993:0858`，序列号 `20240307110322`。Linux 当前视频节点为 `/dev/video4`，稳定标识为 `/dev/v4l/by-id/usb-icSpring_icspring_camera_20240307110322-video-index0`。节点编号会随插拔变化，因此 Linux 按 `config.json` 中的身份自动查找；找不到、匹配不唯一或手动索引不匹配时直接报错，不回退到内置相机。

Windows 的 OpenCV 索引与 Linux 不通用，必须现场确认后显式传入；示例索引 `1` 仅为占位值。Windows 当前只检查指定索引的画面，不声称已验证其 USB 身份。

打开后丢弃 15 帧供曝光稳定，输出首帧灰度最小值、最大值、平均值、标准差。灰度最大值不超过 5 或标准差小于 1 时，自检记为 FAIL，拍摄/预览提示警告但保留图像供排查。这个保守阈值不能区分遮挡、暗场和故障，也不能凭亮度判断相机身份。

本次外接相机实拍为 `640×480`，灰度范围 `6～98`，平均 `15.44`，标准差 `11.08`；画面偏暗但可见物体轮廓，并非全黑。本次内置摄像头也能生成非黑画面，因此不能用“有像素”代替身份校验。未修改相机曝光、增益或分辨率。
