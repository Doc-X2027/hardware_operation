# 三轴力传感器（ART-DAQ）

本目录从 `E:\Code_file\pythonProject_IRS\example_force.py` 追溯整理。原 `force_sensor.py` 源码不存在，只有 `__pycache__/force_sensor.cpython-312.pyc`；它已保存在 `legacy/`，`force_sensor.py` 负责加载并导出原 `ForceSensor` 类。因此本目录须使用 **Windows x64 的 Python 3.12**。

`artdaq/` 是从本机 ART-DAQ 安装目录复制的 Python 库，`native/Art_DAQ.dll` 是对应 x64 用户态库。计算机仍须安装 ART-DAQ 驱动、连接采集卡，且驱动中存在 `Dev1`。这份目录不能替代设备驱动安装。

原模块配置三路模拟电压输入 `Dev1/ai0`、`Dev1/ai1`、`Dev1/ai2`，采样率 `1000 Hz`，默认灵敏度 `20 N/V`。零点校准取 100 次采样。请以实际接线、量程和传感器标定数据核对这些数值；读数顺序为 `Fx, Fy, Fz`，单位 N。

## 调用指令

在本仓库根目录使用 PowerShell：

```powershell
py -3.12 -m pip install -r .\force_sensor\requirements.txt
py -3.12 .\force_sensor\control.py once
py -3.12 .\force_sensor\control.py --zero-calib average 10
py -3.12 .\force_sensor\control.py --zero-calib stream --limit 100
```

`--zero-calib` 会在初始化时采样零点，校准时应让传感器处于指定的无载状态。需要使用现场标定的灵敏度时，在子命令前传入 `--sensitivity`，例如 `--sensitivity 18.5`。不指定 `--limit` 的 `stream` 可用 `Ctrl+C` 结束。无论正常退出还是中断，命令都会调用 `sensor.close()`。

原始用法示例仍可运行：

```powershell
py -3.12 .\force_sensor\example_force.py
```

它执行零点校准、单次读取、10 次平均读取，再连续采集；任一轴绝对值超过 100 N 时退出。`ai_voltage.py` 是 `Dev1/ai2` 的原始电压诊断示例，可用 `py -3.12 .\force_sensor\ai_voltage.py` 执行。`force_sensor_adapter.py` 将三轴力扩展为六维接口供机械臂力控示例使用，后三个力矩值恒为零；机械臂目录也保留了一份适配器以维持原脚本布局。

仅验证了 Python 模块导入、参数解析和离线电压到力的换算；实际采集结果需要连接设备验证。
