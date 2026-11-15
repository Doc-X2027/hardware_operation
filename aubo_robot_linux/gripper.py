"""Control the configured Modbus_0 gripper through the AUBO RPC controller."""

import argparse
import os
import sys


def control_gripper(register, signal, action):
    """Use an existing output register; never create or replace its mapping."""
    names = list(register.modbusGetSignalNames())
    types = list(register.modbusGetSignalTypes())
    if signal not in names:
        raise RuntimeError(f"未找到信号 {signal}；请先在示教器配置 DEVICE_0、地址 10、寄存器输出")
    if len(types) != len(names):
        raise RuntimeError("Modbus 信号列表发生变化，请重新查询")
    if types[names.index(signal)] != 3:
        raise RuntimeError(f"{signal} 不是寄存器输出（类型 3），拒绝写入")
    error = register.modbusGetSignalError(signal)
    if action == "status":
        value = register.modbusGetSignalStatus(signal)
        print(f"signal={signal} value={value} modbus_error={error}")
        if error != 0 or value < 0:
            raise RuntimeError("信号读取异常，请检查示教器 Modbus 配置及通信状态")
        return
    values = {"grip": 0, "release": 1000}
    value = values[action]
    if error != 0:
        raise RuntimeError(f"{signal} Modbus 通信错误码 {error}，未发送指令")
    result = register.modbusSetOutputSignal(signal, value)
    if result != 0:
        raise RuntimeError(f"写入失败，SDK 返回 {result}；请检查控制器状态，勿自动重试")
    print(f"控制器已接受指令：{signal}={value}（{'夹持' if value == 0 else '断开'}）；不代表夹爪动作已完成")


def main(argv=None, sdk=None):
    parser = argparse.ArgumentParser(description="通过机械臂已有 Modbus 信号控制夹爪")
    parser.add_argument("--ip", default=os.getenv("AUBO_IP", "192.168.34.10"))
    parser.add_argument("--port", type=int, default=30004)
    parser.add_argument("--user", default=os.getenv("AUBO_USER", "aubo"))
    parser.add_argument("--password", default="123456")
    parser.add_argument("--signal", default="Modbus_0", help="已配置的寄存器输出信号名")
    parser.add_argument("action", choices=("status", "grip", "release"),
                        help="status 查询；grip 夹持(0)；release 断开(1000)")
    args = parser.parse_args(argv)
    if not args.password or not args.signal.strip():
        parser.error("密码和信号名不能为空")
    if not 1 <= args.port <= 65535:
        parser.error("--port 必须在 1 到 65535 之间")
    if sdk is None:
        from sdk_loader import load_sdk
        sdk = load_sdk()
    client = sdk.RpcClient()
    try:
        client.setRequestTimeout(3000)
        client.connect(args.ip, args.port)
        if not client.hasConnected():
            raise ConnectionError(f"连接失败：{args.ip}:{args.port}")
        client.login(args.user, args.password)
        if not client.hasLogined():
            raise PermissionError("机械臂登录失败")
        control_gripper(client.getRegisterControl(), args.signal, args.action)
    finally:
        if client.hasConnected():
            try:
                if client.hasLogined():
                    client.logout()
            finally:
                client.disconnect()


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"夹爪控制失败：{exc}", file=sys.stderr)
        sys.exit(1)
