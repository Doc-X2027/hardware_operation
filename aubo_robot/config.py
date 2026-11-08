# config.py
# 集成示例：展示 AuboRobot、力传感器、海康相机等模块的组合使用方式

import numpy as np
from aubo_robot import AuboRobot
from force_sensor import ForceSensor
import hikvision

ROBOT_IP   = "192.168.34.10"
ROBOT_PORT = 30004


def config():
    """完整配置示例：力传感器 + 相机 + 机械臂运动"""

    # ========================
    # 1. 力传感器
    # ========================
    sensor = ForceSensor(zero_calib=True)

    fx, fy, fz = sensor.read_one()
    print(f"力: Fx={fx:.2f}N, Fy={fy:.2f}N, Fz={fz:.2f}N")

    fx_list, fy_list, fz_list = sensor.read_n(10)
    print(f"平均力: Fx={np.mean(fx_list):.2f}N; Fy={np.mean(fy_list):.2f}N; Fz={np.mean(fz_list):.2f}N")

    sensor.read_continuous(callback=lambda f: print(f"力: Fx={f[0]:.2f}N, Fy={f[1]:.2f}N, Fz={f[2]:.2f}N"))
    sensor.read_sensor_with_restrict(callback=lambda f: print(f"力: Fx={f[0]:.2f}N, Fy={f[1]:.2f}N, Fz={f[2]:.2f}N"))

    sensor.close()

    # ========================
    # 2. 海康相机拍照
    # ========================
    hikvision.capture_image("A")
    newest_pic = hikvision.get_latest_image(r"C:\Users\DELL\Desktop\photo")
    print(f"最新照片: {newest_pic}")

    # ========================
    # 3. 机械臂 — 使用 AuboRobot 类
    # ========================
    robot = AuboRobot(ROBOT_IP, ROBOT_PORT)
    robot.connect()
    if not robot.is_connected:
        print("RPC客户端连接失败!")
        return

    robot.login("aubo", "123456")

    # 查看状态
    robot.print_state()

    # 夹爪控制
    robot.set_gripper(True)   # 夹紧
    robot.set_gripper(False)  # 松开

    # 绝对直线运动
    robot.move_line([0.551, -0.124, 0.419, -3.134, 0.004, 1.567], speed=1.2, acceleration=0.25, blend_radius=0,
                  async_move=False)

    # 相对直线运动
    robot.move_line_relative([0.01, 0.01, 0.0, 0.0, 0.0, 0.0])

    robot.logout()
    robot.disconnect()


if __name__ == '__main__':
    config()

