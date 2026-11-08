#! /usr/bin/env python
# coding=utf-8

"""
Aubo 机械臂简单运动演示

这是一个最小化的示例，展示如何使用 AuboRobot 类完成一次移动。
默认使用**模拟模式**（离线），如需连接真实机械臂请使用 --real。
"""

import argparse
import sys
from aubo_robot import AuboRobot

ROBOT_IP = "192.168.34.10"
ROBOT_PORT = 30004


def main():
    parser = argparse.ArgumentParser(description="Aubo 机械臂简单运动演示")
    parser.add_argument("--real", action="store_true", help="真实模式（连接实际机械臂）")
    parser.add_argument("--ip", type=str, default=ROBOT_IP, help="控制器 IP")
    parser.add_argument("--port", type=int, default=ROBOT_PORT, help="RPC 端口")
    args = parser.parse_args()

    mock_mode = not args.real

    print("=" * 40)
    print(f"  模式: {'MOCK 模拟' if mock_mode else 'REAL 真实'}")
    print(f"  目标: {args.ip}:{args.port}")
    print("=" * 40)

    # ---- 创建机器人并连接 ----
    robot = AuboRobot(ip=args.ip, port=args.port, mock=mock_mode)

    try:
        robot.connect()
        robot.login()

        # ---- 打印当前状态 ----
        print("\n[1] 当前 TCP 位姿:")
        tcp = robot.get_tcp_pose()
        print(f"    {[round(v, 4) for v in tcp]}")

        # ---- 绝对直线运动 ----
        print("\n[2] 绝对直线运动 → 预设位姿1...")
        robot.move_line(AuboRobot.PRESET_POSE_1)

        # ---- 相对直线运动 ----
        print("\n[3] 相对直线运动 → X+2cm...")
        robot.move_line_relative([0.02, 0.0, 0.0, 0.0, 0.0, 0.0])

        print("\n[完成] 演示结束!")

    except Exception as e:
        print(f"[失败] {e}")
        return 1
    finally:
        robot.logout()
        robot.disconnect()

    return 0


if __name__ == "__main__":
    sys.exit(main())
