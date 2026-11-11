# AUBO 机械臂 Linux 工具

默认登录密码已恢复为原始值 `123456`，无需设置密码环境变量；`control.py` 可通过 `--password` 显式覆盖。
适用 Linux x86_64、CPython 3.12。SDK 版本为 0.26.0rc6。

## 来源与文件

实际部署项目为 `/home/liam/research/VLA_deploy`（本机不存在 `/research/VLA_deploy`）。
SDK 从 `/home/liam/miniconda3/envs/lerobot/lib/python3.12/site-packages/` 复制，
`lib/` 包含 Linux `.so` 和原安装包元数据，不依赖原项目目录。
动态依赖使用系统的 libc、libstdc++、libm、libgcc、libpthread。

- `control.py`：从部署项目的 `hardware/aubo_robot/control.py` 迁入，支持查询、上电、启动、断电、关节及直线运动。运动参数保持部署版的加速度、速度顺序。
- `session.py`：从部署项目迁入的连接与原始状态读取封装。
- `read_state.py`：独立 JSON 状态读取入口，可输出文件，不依赖 VLA 模型配置。
- `sdk_loader.py`：加载本目录 `lib/` 中的 SDK。
- `check_sdk.py`：离线检查 SDK 导入。
- `run.sh`：默认使用 `$HOME/miniconda3/envs/lerobot/bin/python`，可通过 `AUBO_PYTHON` 指定其他 Python 3.12 解释器绝对路径。

## 使用

在仓库根目录执行：

```bash
./aubo_robot_linux/run.sh check_sdk.py
./aubo_robot_linux/run.sh control.py status
./aubo_robot_linux/run.sh read_state.py --output /tmp/aubo-state.json
./aubo_robot_linux/run.sh control.py --help
```

默认地址 `192.168.34.10:30004`，用户名 `aubo`。可设置 `AUBO_IP`、`AUBO_USER`，
或使用 `--ip`、`--port`、`--user`。`control.py` 的公共参数放在子命令前。
状态输出文件采用独占创建，不覆盖已有文件。

需要操作机械臂时，显式使用 `power-on`、`startup`、`power-off`、`move-joint` 或 `move-line`。
运动不会自动上电或启动，要求状态为 `Running`。
`move-joint` 的六个角度为度，速度为度/秒，加速度为度/秒²；
`move-line` 为 x y z roll pitch yaw，位置单位米、姿态单位弧度，速度米/秒、加速度米/秒²。
目标位置需根据现场确认；超时后检查控制器状态，勿直接重复运动命令。

原 `../aubo_robot/demo_arm_move.py` 依赖缺失的 `AuboRobot` 类，未作为可运行脚本迁入。
本目录使用直接调用 SDK 的控制入口。原 Windows 目录保持不变。

已验证本目录 SDK 导入、动态库依赖、脚本语法和 CLI 帮助；未连接或操作真实机械臂。
部署项目记录控制器接口为 0.24.0，全部运动接口的兼容性仍需现场验证。
