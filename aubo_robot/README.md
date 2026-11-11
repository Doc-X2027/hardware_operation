# AUBO 机械臂

默认登录密码已恢复为原始值 `123456`，无需设置密码环境变量；`control.py` 可通过 `--password` 显式覆盖。
本目录来自 `E:\Code_file\pythonProject_IRS`。当前控制器地址已按现场信息更新为 `192.168.34.10:30004`，具体设备若不同，用 `--ip`、`--port` 指定。

## 环境

- Windows x64、Python 3.12。目录内的 `pyaubo_sdk.cp312-win_amd64.pyd` 是从源项目虚拟环境复制的 0.26.0rc6 绑定；Python 3.13 无法加载此文件。
- `aubo_sdk-0.26.0-rc.6-Windows_AMD64+d2cc0fb/` 是原版 C++ SDK，含库、头文件、文档和官方示例。其下还有一层同名目录。
- 连接真实机械臂前确认控制器地址、工作空间、TCP、速度限制及人员安全。仓库内的示例坐标和关节角不能直接视为现场安全轨迹。

从仓库根目录在 PowerShell 中运行：

```powershell
py -3.12 aubo_robot/control.py status
py -3.12 aubo_robot/control.py power-on
py -3.12 aubo_robot/control.py startup
py -3.12 aubo_robot/control.py status
py -3.12 aubo_robot/control.py move-joint 0 -15 100 25 90 0 --speed 20 --acc 20
py -3.12 aubo_robot/control.py move-line 0.551 -0.124 0.419 -3.134 0.004 1.567 --speed 0.05 --acc 0.05
py -3.12 aubo_robot/control.py power-off
```

以上运动数值来自原 SDK 示例，仅用于说明参数格式，必须按现场标定结果替换。`move-joint` 的六个关节角单位是度，速度单位是度/秒，加速度是度/秒²；`move-line` 的位置单位是米，姿态单位是弧度，速度单位是米/秒，加速度是米/秒²。运动前需确认状态为 `Running`。`power-on` 与 `startup` 是两个独立命令，运动命令不会自动上电。运动等待默认 60 秒，可用 `--timeout` 调整。超时后应检查控制器状态，不要直接重复下发运动。

`control.py` 通过 `RpcClient.connect`、`login`、`getRobotInterface` 调用 `getRobotManage()`、`getRobotState()` 和 `getMotionControl()`。退出时会注销并断开 RPC 连接。只有连接真实控制器才能验证上电、启动、运动和断电结果。

## 原项目脚本

| 文件 | 用途 |
| --- | --- |
| `startup.py` | 上电、启动及断电示例；运行主程序会连续执行上电和断电。 |
| `Joint_Moment.py`、`draw_joint_moment.py` | 关节力矩读取和绘图。 |
| `daona_force_control.py`、`force_sensor_adapter.py`、`daona_main.py` | 力控与导纳控制实验。 |
| `pick_and_place_main.py` | 视觉抓取放置任务。 |
| `demo.py`、`demo_arm_move.py`、`config.py` | 原项目的集成和演示脚本。 |

原项目没有 `aubo_robot.py`、`aubo_move.py`、`admittance_controller.py` 源文件，因此引用 `AuboRobot` 或这些模块的脚本目前无法独立运行。力传感器的 Python 3.12 编译模块现已迁入 `../force_sensor/`。`hikvision.py` 已迁入 `../socket_camera/`，但 `pick_and_place_main.py` 和 `config.py` 仍沿用原导入写法；前者也依赖未迁移的 `prompt.py`。这些脚本作为原始资料迁移，实际调用请优先使用 `control.py` 或 SDK 官方示例。工作流文件未迁移。
