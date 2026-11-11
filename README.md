# 硬件调用脚本

main 分支保存普通设备脚本：

- [AUBO 机械臂](aubo_robot/README.md)
- [网络相机](socket_camera/README.md)
- [USB 相机](usb_camera/README.md)
- 三轴力传感器：force_sensor/

AUBO 默认登录密码为 `123456`。

Linux 专用脚本、配置、库及综合自检保存在 `feat/linux_plugin` 分支：

- `aubo_robot_linux/`
- `socket_camera_linux/`
- `usb_camera_linux/`
- `self_check.py` 和相关测试

切换到 Linux 开发环境：

```bash
git switch feat/linux_plugin
```

切回普通脚本：

```bash
git switch main
```
