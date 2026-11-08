# USB 相机调用

`shijue.py` 使用 OpenCV 的相机索引 `0` 读取 USB 摄像头，并按 HSV 颜色范围识别红、绿、蓝、黄物块。新增的 `control.py` 提供独立调用入口。先从本仓库根目录安装依赖：

```powershell
python -m pip install -r .\usb_camera\requirements.txt
```

拍摄一帧并保存：

```powershell
python .\usb_camera\control.py capture --output .\usb_photo.jpg
```

识别红色物块并保存标注图片：

```powershell
python .\usb_camera\control.py detect 红 --output .\usb_red.jpg
```

相机索引不为 `0` 时，在子命令前加入 `--index`，如 `python .\usb_camera\control.py --index 1 capture --output .\usb_photo.jpg`。识别结果为图像像素坐标和角度；`shijue.py` 中的 `calibrate()` 目前只是原值返回，不能直接当作机械臂坐标使用。颜色阈值需按现场光照校准。

`zhuaqu_main_cv.py` 是原项目的视觉抓取流程脚本，还依赖源项目中的 `prompt.py` 和未找到的 `voice.py`，目前不能独立运行；机械臂移动部分也仍为注释和打印。
