# Windows USB 相机拍摄与取流

本目录使用 OpenCV 原生窗口，面向 Windows；Linux 请使用独立目录 [usb_camera_linux](https://github.com/Doc-X2027/hardware_operation/blob/feat/linux_plugin/usb_camera_linux/README.md)，其 GTK 预览与 `socket_camera_linux` 一致。拍摄和无窗口取流代码跨平台，图形预览按平台分别实现，两个目录可独立运行。

## 安装及运行

从仓库根目录执行，无需 GTK 或相机厂商 SDK。使用带图形界面的 `opencv-python`，不要使用 `opencv-python-headless`。

```powershell
python -m pip install -r .\usb_camera\requirements.txt

# 拍摄一帧，自动创建输出目录
python .\usb_camera\control.py --index 1 capture --output .\usb_camera\captures\frame.png

# 持续取流并预览
python .\usb_camera\control.py --index 1 stream

# 选择相机；索引因设备和系统而异
python .\usb_camera\control.py --index 1 stream

# 无窗口采集 100 帧
python .\usb_camera\control.py --index 1 stream --headless --frames 100

# 修改连续读取失败上限
python .\usb_camera\control.py --index 1 stream --max-failures 5
```

Windows 必须显式提供 `--index`，放在子命令前；不再默认打开索引 0。`--frames 0`（默认）持续取流，Ctrl+C 停止；连续读取失败默认达到 5 次后报错退出，成功读取后重置失败计数。使用设备默认分辨率和帧率，读取阻塞时长由设备驱动和 OpenCV 后端决定。

## 预览窗口交互

- 初始窗口 1200×800，可调整大小；图像保持比例居中，背景为深色。
- 鼠标上滚放大、下滚缩小，每步 1.15 倍，缩放范围为适配窗口比例的 0.05～50 倍。
- 鼠标中键恢复适配窗口；放大后超出窗口部分裁剪，标题显示当前倍率。
- S 保存完整分辨率的当前帧到工作目录 `usb_camera_<索引>.jpg`，再次按 S 覆盖同名文件。
- Q / Esc 或关闭窗口退出。

Windows 滚轮使用 OpenCV HighGUI 鼠标回调；Linux GTK 版本还支持触控板平滑滚动。本次开发环境为 Linux，Windows 预览尚未进行实机验证。

## 自检

从仓库根目录执行，检查 USB 依赖及单帧读取：

```powershell
# 综合自检请切换至 feat/linux_plugin 分支后运行
py -3.12 self_check.py --skip-robot --skip-gige --skip-force --usb-index 1
```

多台相机可使用 `--usb-index 1 4`（索引按实际设备替换）；添加 `--check-preview` 检查窗口环境，添加 `--offline` 仅检查文件和依赖。自检不保存图片，默认每项超时 5 秒，详见 [根目录自检说明](../README.md#自检参数与结果)。

## 外接相机身份与画面检查（2026-11-10）

目标为 `icSpring / icspring camera`，USB VID:PID `2993:0858`，序列号 `20240307110322`。Linux 当前视频节点为 `/dev/video4`，稳定标识为 `/dev/v4l/by-id/usb-icSpring_icspring_camera_20240307110322-video-index0`。节点编号会随插拔变化，因此 Linux 按 `config.json` 中的身份自动查找；找不到、匹配不唯一或手动索引不匹配时直接报错，不回退到内置相机。

Windows 的 OpenCV 索引与 Linux 不通用，必须现场确认后显式传入；示例索引 `1` 仅为占位值。Windows 当前只检查指定索引的画面，不声称已验证其 USB 身份。

打开后丢弃 15 帧供曝光稳定，输出首帧灰度最小值、最大值、平均值、标准差。灰度最大值不超过 5 或标准差小于 1 时，自检记为 FAIL，拍摄/预览提示警告但保留图像供排查。这个保守阈值不能区分遮挡、暗场和故障，也不能凭亮度判断相机身份。

本次外接相机实拍为 `640×480`，灰度范围 `6～98`，平均 `15.44`，标准差 `11.08`；画面偏暗但可见物体轮廓，并非全黑。本次内置摄像头也能生成非黑画面，因此不能用“有像素”代替身份校验。未修改相机曝光、增益或分辨率。
