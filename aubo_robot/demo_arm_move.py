#! /usr/bin/env python
# coding=utf-8

"""
机械臂移动演示脚本

演示如何使用 aubo_robot 模块完成一次完整的机械臂运动序列。
默认使用**模拟模式**离线运行（无需连接真实机械臂）。

使用方式:
    python demo_arm_move.py              # 模拟模式（默认）
    python demo_arm_move.py --mock       # 显式指定模拟模式
    python demo_arm_move.py --real       # 真实模式（需配置IP和连接机械臂）

网络配置（真实模式）:
    修改下方 ROBOT_IP / ROBOT_PORT 为实际机械臂控制器地址
"""

import argparse
import time
import math
import sys

from aubo_robot import AuboRobot, _deg_to_rad, _rad_to_deg

# =========================================================================
# 网络配置（仅在真实模式下使用）
# =========================================================================
ROBOT_IP = "192.168.34.10"   # 当前机械臂控制器 IP
ROBOT_PORT = 30004            # RPC 端口

# =========================================================================
# 运动参数
# =========================================================================
SPEED_FRACTION = 0.75         # 速度比率 (0~1)
LINE_SPEED = 1.2              # 直线运动工具速度 [m/s]
LINE_ACC = 0.25               # 直线运动工具加速度 [m/s²]
JOINT_SPEED = _deg_to_rad(80) # 关节速度 [rad/s]
JOINT_ACC = _deg_to_rad(60)   # 关节加速度 [rad/s²]


def demo_single_move(robot):
    """演示: 单次绝对直线运动"""
    print("\n" + "─" * 50)
    print("[TASK] 任务1: 单次绝对直线运动")
    print("─" * 50)

    pose = [0.551, -0.124, 0.419, -3.134, 0.004, 1.567]
    print(f"   目标位姿: {pose}")
    ok = robot.move_line(pose, speed=LINE_SPEED, acceleration=LINE_ACC)
    status = "[OK] 成功" if ok else "[FAIL] 失败"
    print(f"   结果: {status}")
    return ok


def demo_relative_move(robot):
    """演示: 相对直线运动"""
    print("\n" + "─" * 50)
    print("[TASK] 任务2: 相对直线运动")
    print("─" * 50)

    # 获取当前位姿
    current = robot.get_tcp_pose()
    if current:
        print(f"   当前 TCP 位姿: {[round(v, 4) for v in current]}")

    delta = [0.02, 0.0, 0.0, 0.0, 0.0, 0.0]  # X 方向移动 2cm
    print(f"   偏移量: {delta}")

    ok = robot.move_line_relative(delta, speed=LINE_SPEED, acceleration=LINE_ACC)
    status = "[OK] 成功" if ok else "[FAIL] 失败"
    print(f"   结果: {status}")
    return ok


def demo_multi_point_path(robot):
    """演示: 多点连续轨迹 — 依次走 3 个路点"""
    print("\n" + "─" * 50)
    print("[TASK] 任务3: 多点连续直线轨迹")
    print("─" * 50)

    waypoints = [
        AuboRobot.PRESET_POSE_1,
        AuboRobot.PRESET_POSE_2,
        AuboRobot.PRESET_POSE_3,
    ]

    for i, pose in enumerate(waypoints, 1):
        print(f"\n   -> 路点 {i}: {[round(v, 4) for v in pose]}")
        ok = robot.move_line(pose, speed=LINE_SPEED, acceleration=LINE_ACC)
        if not ok:
            print(f"   [FAIL] 路点 {i} 失败，停止后续运动")
            return False
        print(f"   [OK] 路点 {i} 到达")

    print("\n   多点连续轨迹完成!")
    return True


def demo_joint_then_line(robot):
    """演示: 先关节运动回原点，再直线运动到目标"""
    print("\n" + "─" * 50)
    print("[TASK] 任务4: 关节运动回原点 + 直线运动到目标")
    print("─" * 50)

    # 第一步：关节运动到安全起始位置
    home = AuboRobot.PRESET_HOME_JOINT
    print(f"\n   步骤A: 关节运动回原点 (角/度): {[_rad_to_deg(v) for v in home]}")
    print(f"          关节角 (弧度): {[round(v, 4) for v in home]}")
    ok = robot.move_joint(home, speed=JOINT_SPEED, acceleration=JOINT_ACC)
    if not ok:
        print("   [FAIL] 关节运动失败")
        return False
    print("   [OK] 关节运动完成，已到达原点")

    # 第二步：直线运动到第一个目标
    target = AuboRobot.PRESET_POSE_1
    print(f"\n   步骤B: 直线运动到目标位姿 {[round(v, 4) for v in target]}")
    ok = robot.move_line(target, speed=LINE_SPEED, acceleration=LINE_ACC)
    if not ok:
        print("   [FAIL] 直线运动失败")
        return False
    print("   [OK] 直线运动完成")

    return True


def demo_pick_and_place(robot):
    """演示: 模拟「取放」动作序列

    1. 移动到取料点上方 (approach)
    2. 下降取料 (pick)
    3. 抬起 (retract)
    4. 移动到放料点上方
    5. 下降放料 (place)
    6. 抬起回到安全位
    """
    print("\n" + "─" * 50)
    print("[TASK] 任务5: 模拟「取放」动作序列")
    print("─" * 50)

    # 从当前位置开始，先回原点
    home = AuboRobot.PRESET_HOME_JOINT
    robot.move_joint(home, speed=JOINT_SPEED, acceleration=JOINT_ACC)

    # 取料点基准位姿（从预设位姿1开始）
    base = AuboRobot.PRESET_POSE_1[:]
    pick_approach = base[:]
    pick_point = base[:]
    pick_point[2] -= 0.05        # 下降 5cm 取料

    place_base = [0.552, 0.235, 0.419, -3.138, 0.007, 1.567]
    place_approach = place_base[:]
    place_point = place_base[:]
    place_point[2] -= 0.05       # 下降 5cm 放料

    steps = [
        ("接近取料点", pick_approach, "line"),
        ("取料（下降）", pick_point,   "line"),
        ("抬起",        pick_approach, "line"),
        ("移向放料点",  place_approach, "line"),
        ("放料（下降）", place_point,   "line"),
        ("回到安全位",  place_approach, "line"),
    ]

    for name, target, move_type in steps:
        print(f"   {name}: {[round(v, 4) for v in target]}")
        if move_type == "line":
            ok = robot.move_line(target, speed=LINE_SPEED, acceleration=LINE_ACC)
        else:
            ok = robot.move_joint(target, speed=JOINT_SPEED, acceleration=JOINT_ACC)

        if not ok:
            print(f"   [FAIL] '{name}' 失败")
            return False
        print(f"   [OK] '{name}' 完成")
        time.sleep(0.1)

    print("\n   「取放」序列全部完成!")
    return True


# =========================================================================
# 主入口
# =========================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Aubo 机械臂运动演示",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python demo_arm_move.py                # 模拟模式
  python demo_arm_move.py --mock         # 模拟模式（显式）
  python demo_arm_move.py --real         # 真实模式（连接机械臂）
  python demo_arm_move.py --ip 10.0.0.5  # 指定 IP 的真实模式
        """,
    )
    parser.add_argument(
        "--mock", action="store_true", default=False,
        help="模拟模式（离线运行，不连接机械臂）"
    )
    parser.add_argument(
        "--real", action="store_true", default=False,
        help="真实模式（连接实际机械臂）"
    )
    parser.add_argument(
        "--ip", type=str, default=None,
        help=f"机械臂控制器 IP（默认 {ROBOT_IP}）"
    )
    parser.add_argument(
        "--port", type=int, default=ROBOT_PORT,
        help=f"RPC 端口（默认 {ROBOT_PORT}）"
    )
    args = parser.parse_args()

    # 确定模式
    if args.real:
        mock_mode = False
    elif args.mock:
        mock_mode = True
    else:
        # 默认模拟模式
        mock_mode = True

    ip = args.ip if args.ip else ROBOT_IP

    # ---- 打印运行信息 ---------------------------------------------------
    print("=" * 60)
    print("  Aubo 机械臂运动演示")
    print("=" * 60)
    if mock_mode:
        print(f"  模式: [MOCK] 模拟模式 (离线)")
        print(f"  提示: 所有运动均为日志模拟，无需真实硬件")
    else:
        print(f"  模式: [REAL] 真实模式")
        print(f"  目标: {ip}:{args.port}")
    print("=" * 60)

    # ---- 初始化机器人 ---------------------------------------------------
    robot = AuboRobot(ip=ip, port=args.port, mock=mock_mode)

    try:
        # 连接 & 登录
        print("\n[CONNECT] 连接机械臂...")
        if not robot.connect():
            print("[FAIL] 连接失败，退出")
            return 1

        if not robot.login():
            print("[FAIL] 登录失败，退出")
            return 1

        # 基础设置
        robot.set_speed_fraction(SPEED_FRACTION)
        robot.set_tcp_offset()

        # 打印当前状态
        print("\n[STATUS] 初始状态:")
        tcp = robot.get_tcp_pose()
        joints = robot.get_joint_positions()
        if tcp:
            print(f"   TCP 位姿: {[round(v, 4) for v in tcp]}")
        if joints:
            print(f"   关节角:   {[round(_rad_to_deg(v), 2) for v in joints]} (度)")

        # ---- 依次执行演示任务 -------------------------------------------
        tasks = [
            ("单次绝对直线运动",           demo_single_move),
            ("相对直线运动",               demo_relative_move),
            ("多点连续直线轨迹",           demo_multi_point_path),
            ("关节运动+直线运动",          demo_joint_then_line),
            ("取放动作序列",               demo_pick_and_place),
        ]

        results = {}
        for name, func in tasks:
            try:
                ok = func(robot)
                results[name] = "[OK]" if ok else "[FAIL]"
            except Exception as e:
                print(f"\n   [FAIL] 异常: {e}")
                results[name] = "[FAIL]"

        # ---- 汇总 -------------------------------------------------------
        print("\n" + "=" * 60)
        print("  演示汇总")
        print("=" * 60)
        for name, status in results.items():
            print(f"   {status}  {name}")
        print("=" * 60)

    except KeyboardInterrupt:
        print("\n[WARN] 用户中断")

    except Exception as e:
        print(f"\n[FAIL] 未预期异常: {e}")
        return 1

    finally:
        # 安全退出
        print("\n[DISCONNECT] 登出并断开连接...")
        robot.logout()
        robot.disconnect()
        print("Done - 演示结束\n")

    return 0 if all(v == "[OK]" for v in results.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
