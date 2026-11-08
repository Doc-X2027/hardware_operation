#! /usr/bin/env python
# coding=utf-8

"""
力控示例

步骤:
第一步: 连接RPC服务器、登录
第二步: 开启力传感器标定并开启力控模式
第三步: 退出登陆并断开RPC连接
"""
import pyaubo_sdk
import time
import csv
import math
import sys
sys.path.append(".")
from force_sensor_adapter import ForceSensorAdapter
from force_sensor import ForceSensor
from typing import List, Sequence, Tuple, Any, Optional

robot_ip = "192.168.34.10"  # 服务器 IP 地址
robot_port = 30004  # 端口号
M_PI = 3.14159265358979323846
robot_rpc_client = pyaubo_sdk.RpcClient()
EMBEDDED: bool = False # 是否使用机械臂内置力传感器
SENSOR_VENDOR: str = "external_3d_force_sensor"  # 外置力传感器

# 拖动示教
M1 = [30.0, 30.0, 30.0]
D1 = [1000.0, 1000.0, 1000.0]
K1 = [0, 0, 0]
goal_force1 = 0
# 弹簧效果
M2 = [30.0, 30.0, 30.0]
D2 = [1000.0, 1000.0, 100.0]
K2 = [100.0, 100.0, 100.0]
goal_force2 = 0
# 恒力打磨
M3 = [30.0, 30.0, 30.0]
D3 = [1000.0, 1000.0, 100.0]
K3 = [1000.0, 1000.0, 0]
goal_force3 = -5

M = [M1, M2, M3]
D = [D1, D2, D3]
K = [K1, K2, K3]
goal_force = [goal_force1, goal_force2, goal_force3]
# 阻塞
def wait_arrival(robot_interface):
    max_retry_count = 5
    cnt = 0

    # 接口调用: 获取当前的运动指令 ID
    exec_id = robot_interface.getMotionControl().getExecId()

    # 等待机械臂开始运动
    while exec_id == -1:
        if cnt > max_retry_count:
            return -1
        time.sleep(0.05)
        cnt += 1
        exec_id = robot_interface.getMotionControl().getExecId()

    # 等待机械臂运动完成
    while robot_interface.getMotionControl().getExecId() != -1:
        time.sleep(0.05)

    return 0

def calculate_distance(p1: Sequence[float], p2: Optional[Sequence[float]] = None) -> float:
    """
    计算两点之间的欧氏距离，默认第二点为原点
    """
    if p2 is None:
        p2 = (0.0,) * 6
    if len(p1) != 6 or len(p2) != 6:
        return 0.0
    return math.sqrt(sum((p1[i] - p2[i]) ** 2 for i in range(3)))

def fc_enable(cli: Any)->int:
    # 接口调用：获取机器人的名字
    robot_name = cli.getRobotNames()[0]
    robot = cli.getRobotInterface(robot_name)
    # 开启力控
    ret = robot.getForceControl().fcEnable()
    print(ret)
    if ret != 0:
        print("力控开启失败, 错误码: ", ret)
        return -1

def fc_disable(cli: Any)->int:
    # 接口调用：获取机器人的名字
    robot_name = cli.getRobotNames()[0]
    robot = cli.getRobotInterface(robot_name)
    # 关闭力控
    ret = robot.getForceControl().fcDisable()
    if ret != 0:
        print("力控关闭失败, 错误码: ", ret)
        return -1

def tcp_sensor_test(cli: Any, csv_path: str = "force.csv"):
    # 接口调用：获取机器人的名字
    robot_name = cli.getRobotNames()[0]

    # 选择力传感器类型
    if EMBEDDED:
        sensor_pose = [0, 0, 0, 0, 0, 0]
        cli.getRobotInterface(robot_name) \
            .getRobotConfig() \
            .selectTcpForceSensor("embedded")
    else:
        sensor_pose = [0, 0, 0.047, 0, 0, 0]
        cli.getRobotInterface(robot_name) \
            .getRobotConfig() \
            .selectTcpForceSensor(SENSOR_VENDOR)

    # 写入 CSV
    with open(csv_path, "a", newline="") as f:
        writer = csv.writer(f)

        # 表头
        writer.writerow(["Fx", "Fy", "Fz", "Tx", "Ty", "Tz"])
        f.flush()

        while True:
            sensor_data = cli.getRobotInterface(robot_name) \
                             .getRobotState() \
                             .getTcpForceSensors()

            print("--------------------------------------")
            for i, v in enumerate(sensor_data):
                print(f"获取TCP力传感器读数: {i + 1}: {v}")
            print("--------------------------------------")

            writer.writerow(list(sensor_data))
            f.flush()

            time.sleep(0.005)

# --------- 力传感器标定 ----------
def tcp_sensor_calibration_3d(cli: Any, joints: List[List[float]], force_sensor_adapter) -> Tuple[
    List[float], List[float], float]:
    """三维力传感器的三点标定"""
    robot_name = cli.getRobotNames()[0]
    robot_interface = cli.getRobotInterface(robot_name)

    calib_forces_3d = []  # 存储三维力数据

    for i, joint in enumerate(joints):
        print(f"goto p{i}")
        robot_interface.getMotionControl().moveJoint(
            joint,
            10.0 * (math.pi / 180.0),
            5.0 * (math.pi / 180.0),
            0, 0
        )
        wait_arrival(robot_interface)
        time.sleep(1.0)

        q = robot_interface.getRobotState().getJointPositions()
        # 使用三维传感器获取力数据
        fx, fy, fz, _, _, _ = force_sensor_adapter.get_force()
        calib_forces_3d.append([fx, fy, fz])

        pose = robot_interface.getRobotAlgorithm().forwardKinematics(q)
        calib_poses = [list(pose[0])]  # 位姿数据

    # 三点标定（转换为六维格式，力矩部分为0）
    calib_forces_6d = [f + [0, 0, 0] for f in calib_forces_3d]
    calib_poses = [calib_poses[0], calib_poses[1], calib_poses[2]]

    # 调用标定接口
    result = robot_interface.getRobotAlgorithm().calibrateTcpForceSensor(calib_forces_6d, calib_poses)
    return result


# --------- 力控模式开启示例 ----------
def example_force_control(cli: Any, force_adapter: ForceSensorAdapter) -> None:
    robot_name = cli.getRobotNames()[0]
    robot_interface = cli.getRobotInterface(robot_name)

    # 使用外置三维力传感器
    sensor_pose = [0.0, 0.0, 0.047, 0.0, 0.0, 0.0]  # 传感器安装位姿
    robot_interface.getRobotConfig().selectTcpForceSensor(SENSOR_VENDOR)
    robot_interface.getRobotConfig().setTcpForceSensorPose(sensor_pose)

    # 设置TCP偏移
    tcp_pose = list(sensor_pose)
    robot_interface.getRobotConfig().setTcpOffset(tcp_pose)

    # 负载辨识参考点
    joint1 = [-0.261799, 0.261799, 1.309, 1.0472, 1.39626, 0.0]
    joint2 = [-0.628319, 0.471239, 1.65806, -0.471239, 0.0, 0.0]
    joint3 = [-0.628319, 0.366519, 1.74533, -0.10472, 1.5708, 0.0]

    # 三维传感器标定
    calib_result = tcp_sensor_calibration_3d(cli, [joint1, joint2, joint3], force_adapter)
    force_offset = calib_result[0]  # 6维偏移量，力矩部分为0
    com = calib_result[1]  # 质心
    mass = calib_result[2]  # 质量

    # ========== 导纳参数（只控制平移，旋转锁定） ==========
    # 只控制平移（X,Y,Z），旋转使用高刚度锁定
    M_trans = M[0]  # 仅X,Y,Z方向质量
    D_trans = D[0]  # 仅X,Y,Z方向阻尼
    K_trans = K[0]  # 仅X,Y,Z方向刚度

    # 旋转方向参数（高刚度锁定）
    M_rot = [100.0, 100.0, 100.0]  # 旋转惯性
    D_rot = [5000.0, 5000.0, 5000.0]  # 旋转阻尼（高阻尼保持稳定）
    K_rot = [5000.0, 5000.0, 5000.0]  # 旋转刚度（高刚度锁定姿态）

    # 组合为6维参数
    admittance_m = M_trans + M_rot
    admittance_d = D_trans + D_rot
    admittance_k = K_trans + K_rot

    robot_interface.getForceControl().setDynamicModel(admittance_m, admittance_d, admittance_k)

    # ========== 目标力和控制自由度 ==========

    # 只控制平移自由度，旋转方向不参与力控
    compliance = [True, True, True, False, False, False]  # 仅X,Y,Z力控
    target_wrench = [0, 0, 0, 0, 0, 0]

    speed_limits = [0.2, 0.2, 0.2, 0.1, 0.1, 0.1]  # 平移0.2m/s，旋转0.1rad/s

    task_frame = pyaubo_sdk.TaskFrameType.NONE

    robot_interface.getForceControl().setTargetForce(
        [0.0] * 6, compliance, target_wrench, speed_limits, task_frame
    )

    print("Press 's'/'q' to enable/disable force control mode.")
    while True:
        key = input("Please input your choose: ").strip()
        if not key:
            continue
        key = key[0]

        if key == "s":
            if robot_interface.getForceControl().isFcEnabled():
                print("The robot has already been force control mode. Can't enable.")
            else:
                fc_enable(cli)
                print("Enter force control mode")

        elif key == "q":
            if not robot_interface.getForceControl().isFcEnabled():
                print("The robot has already quit force control mode. Can't disable.")
            else:
                fc_disable(cli)
                print("Quit force control mode")

        else:
            print("Please input 's' or 'q'.")

if __name__ == '__main__':
    # 初始化三维力传感器
    sensor = ForceSensor(zero_calib=True)
    force_adapter = ForceSensorAdapter(sensor)

    # 进行零点校准
    print("正在进行零点校准，请确保无外力接触...")
    time.sleep(2)
    fx_zero, fy_zero, fz_zero = sensor.read_one()
    force_adapter.set_zero_offset(fx_zero, fy_zero, fz_zero)
    print(f"零点偏移: Fx={fx_zero:.2f}N, Fy={fy_zero:.2f}N, Fz={fz_zero:.2f}N")

    robot_rpc_client.setRequestTimeout(1000)
    robot_rpc_client.connect(robot_ip, robot_port)  # 接口调用: 连接到 RPC 服务
    if robot_rpc_client.hasConnected():
        print("Robot rcp_client connected successfully!")
        robot_rpc_client.login("aubo", "123456")  # 接口调用: 机械臂登录
        if robot_rpc_client.hasLogined():
            print("Robot rcp_client logined successfully!")
            # 使能和退出力控
            example_force_control(robot_rpc_client, force_adapter)
            # 读取力传感器数据并保存到force.csv文件中
            # tcp_sensor_test(robot_rpc_client, "force.csv")