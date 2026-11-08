"""AUBO RPC command line for this hardware setup (Windows, Python 3.12)."""

import argparse
import math
import os
import time


def six_values(values):
    if len(values) != 6 or not all(math.isfinite(value) for value in values):
        raise ValueError("需要 6 个有限数值")
    return values


def wait_for_motion(motion, timeout):
    deadline = time.monotonic() + timeout
    started = False
    while time.monotonic() < deadline:
        exec_id = motion.getExecId()
        if exec_id != -1:
            started = True
        elif started:
            return
        time.sleep(0.05)
    raise TimeoutError("等待运动完成超时；请从控制器确认机械臂状态")


def main():
    parser = argparse.ArgumentParser(description="AUBO 机械臂 RPC 指令")
    parser.add_argument("--ip", default=os.getenv("AUBO_IP", "192.168.34.10"))
    parser.add_argument("--port", type=int, default=30004)
    parser.add_argument("--user", default=os.getenv("AUBO_USER", "aubo"))
    parser.add_argument("--password", default=os.getenv("AUBO_PASSWORD"))
    parser.add_argument("--timeout", type=float, default=60.0, help="运动等待超时，秒")
    actions = parser.add_subparsers(dest="action", required=True)
    for name in ("status", "power-on", "startup", "power-off"):
        actions.add_parser(name)
    joint = actions.add_parser("move-joint", help="6 个关节角，单位为度")
    joint.add_argument("angles", nargs=6, type=float)
    joint.add_argument("--speed", type=float, default=20.0, help="关节速度，度/秒")
    joint.add_argument("--acc", type=float, default=20.0, help="关节加速度，度/秒²")
    line = actions.add_parser("move-line", help="x y z rx ry rz；米、弧度")
    line.add_argument("pose", nargs=6, type=float)
    line.add_argument("--speed", type=float, default=0.05, help="直线速度，米/秒")
    line.add_argument("--acc", type=float, default=0.05, help="直线加速度，米/秒²")
    args = parser.parse_args()
    if not args.password:
        parser.error("请通过 AUBO_PASSWORD 设置控制器密码")
    if args.timeout <= 0:
        parser.error("--timeout 必须大于 0")
    if args.action == "move-joint":
        six_values(args.angles)
    elif args.action == "move-line":
        six_values(args.pose)
    if args.action.startswith("move-") and (not math.isfinite(args.speed) or not math.isfinite(args.acc) or args.speed <= 0 or args.acc <= 0):
        parser.error("--speed 和 --acc 必须为正数")

    import pyaubo_sdk

    client = pyaubo_sdk.RpcClient()
    try:
        client.connect(args.ip, args.port)
        if not client.hasConnected():
            raise ConnectionError(f"连接失败：{args.ip}:{args.port}")
        client.login(args.user, args.password)
        if not client.hasLogined():
            raise PermissionError("机械臂登录失败")
        names = client.getRobotNames()
        if not names:
            raise RuntimeError("控制器未返回机械臂名称")
        robot = client.getRobotInterface(names[0])
        if args.action == "status":
            state = robot.getRobotState()
            print(f"robot={names[0]} mode={state.getRobotModeType().name}")
            print(f"joints_rad={list(state.getJointPositions())}")
            print(f"tool_pose={list(state.getToolPose())}")
        elif args.action == "power-on":
            result = robot.getRobotManage().poweron()
            if result != 0:
                raise RuntimeError(f"上电请求失败，SDK 返回 {result}")
            print("上电请求已发送")
        elif args.action == "startup":
            result = robot.getRobotManage().startup()
            if result != 0:
                raise RuntimeError(f"启动请求失败，SDK 返回 {result}")
            print("启动请求已发送；请用 status 确认 Running 状态")
        elif args.action == "power-off":
            result = robot.getRobotManage().poweroff()
            if result != 0:
                raise RuntimeError(f"断电请求失败，SDK 返回 {result}")
            print("断电请求已发送")
        else:
            motion = robot.getMotionControl()
            if robot.getRobotState().getRobotModeType() != pyaubo_sdk.RobotModeType.Running:
                raise RuntimeError("机械臂未处于 Running 状态")
            if args.action == "move-joint":
                result = motion.moveJoint(
                    [math.radians(v) for v in args.angles],
                    math.radians(args.speed), math.radians(args.acc), 0, 0
                )
            else:
                result = motion.moveLine(args.pose, args.speed, args.acc, 0, 0)
            if result != 0:
                raise RuntimeError(f"运动指令失败，SDK 返回 {result}")
            wait_for_motion(motion, args.timeout)
            print("运动已完成")
    finally:
        if client.hasConnected():
            if client.hasLogined():
                client.logout()
            client.disconnect()


if __name__ == "__main__":
    main()
