# 网络相机调用

此目录包含源项目的两种网络调用方式，它们并非同一个接口。当前 Linux 电脑请使用 [socket_camera_linux](../socket_camera_linux/README.md) 中的 Aravis 取流脚本；该路径已通过真实取流验证，窗口使用 GTK 原生滚轮缩放。此目录保留原 MVS 调用方式。

## 本机 TCP 服务：`hikvision.py`

`hikvision.py` 连接 `127.0.0.1:8888`，向已运行的相机服务发送指令。本仓库没有该服务端程序；必须先启动原有服务。`capture_image("A")` 发送 `A` 并等待响应，图片由服务端保存到原配置目录，客户端不接收图片内容。原脚本查找最新图片时默认使用 `C:\Users\DELL\Desktop\photo`。

从仓库根目录执行：

```powershell
python -c "from socket_camera.hikvision import capture_image; print(capture_image('A'))"
python -c "from socket_camera.hikvision import get_latest_image; print(get_latest_image(r'C:\Users\DELL\Desktop\photo'))"
python -c "from socket_camera.hikvision import find; print(find('pick', 'red'))"
```

`find` 发送两位代码：第一位 `pick=1`、`place=2`；第二位 `red=1`、`green=2`、`blue=3`、`yellow=4`、`orange=5`、`purple=6`。例如 `find('pick', 'red')` 发送 `11`，并返回服务端响应。具体识别结果格式取决于服务端。

## 海康 GigE 相机：`hikrobot_stream.py`

该脚本通过海康 SDK 发现和采集 IP 为 `192.168.34.55` 的相机，不使用上述 `127.0.0.1:8888` 服务。`hikrobot/` 已包含原环境中的 Python 封装（`hikrobot-sdk` 0.1.1）；本机仍需安装海康 MVS 驱动。安装 `requirements-camera.txt` 中的依赖后，可执行：

```powershell
python -m pip install -r .\socket_camera\requirements-camera.txt
python .\socket_camera\hikrobot_stream.py --show-settings
python .\socket_camera\hikrobot_stream.py --output .\camera_192.168.34.55.jpg
```

预览、曝光、增益、拍照和样张说明见 [相机取流与拍照指令.md](相机取流与拍照指令.md)。本目录中的两张 JPG 是原项目的曝光前后对比样张。
