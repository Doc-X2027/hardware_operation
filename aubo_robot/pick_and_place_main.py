#! /usr/bin/env python
# coding=utf-8

"""
机械臂完整抓取放置任务 (Pick & Place)

依赖:
- aubo_move.py    (参考: wait_arrival, moveLine/moveJoint 用法)
- hikvision.py    (视觉定位: find(obj, color))
- prompt.py       (LLM 任务编排: generate_workflow_json)
- startup.py      (参考: poweron/startup/poweroff 流程)

步骤:
第一步: RPC 连接、登录、上电
第二步: LLM 生成任务编排 JSON
第三步: 遍历任务序列执行抓取/放置
第四步: 断电、登出、断开连接
"""

import time
import math
import json
import re
import sys
from datetime import datetime

import pyaubo_sdk
import hikvision
import prompt

# ============================================================
# 常量配置
# ============================================================
ROBOT_IP = "192.168.34.10"
ROBOT_PORT = 30004
ROBOT_USER = "aubo"
ROBOT_PASSWORD = "123456"

# 运动参数
SPEED_FRACTION = 0.5         # 速度比率 (0~1)
LINEAR_SPEED = 0.8           # 直线运动速度 (m/s)
LINEAR_ACC = 0.3             # 直线运动加速度 (m/s²)
JOINT_SPEED = 80 * (math.pi / 180)    # 关节速度 (rad/s)
JOINT_ACC = 60 * (math.pi / 180)      # 关节加速度 (rad/s²)

# 初始关节角 (弧度) —— 安全高度，机械臂抬起远离工作台
INIT_JOINT = [
    -90 * (math.pi / 180),
    0 * (math.pi / 180),
    90 * (math.pi / 180),
    0 * (math.pi / 180),
    90.0 * (math.pi / 180),
    0.0 * (math.pi / 180),
]

# Z 轴下降量 —— 从安全高度到操作高度的距离 (米)
# 需根据实际场景示教调整
PICK_DESCENT = 0.1          # 抓取: 从安全高度下降到方块高度
PLACE_DESCENT = 0.1        # 放置: 从安全高度下降到盘子高度

# 任务描述 (自然语言 → LLM 生成 workflow.json)
TASK_REQUEST = (
    "移动机械臂依次抓取红、绿、蓝、黄、橙、紫色方块，"
    "分别放入红、绿、蓝、黄、紫、橙色盘中"
)

# ============================================================
# 工具函数
# ============================================================


def parse_find_result(raw):
    """
    解析 hikvision.find() 返回值。

    视觉服务器返回格式: #label;x,y,rz 或 #label;x;y;rz
    raw 为 repr(data)，如 "b'#1;-0.012,0.034,-3.5'" 或 "'#1;-0.012;0.034;-3.5'"

    返回:
        (label, dx, dy, drz) 或 None (解析失败)
        dx, dy: 米, drz: 度
    """
    if raw is None:
        return None
    # 兼容分号 / 逗号混合分隔
    match = re.search(
        r'#(\d+)\s*[;,]\s*([-\d.]+)\s*[;,]\s*([-\d.]+)\s*[;,]\s*([-\d.]+)',
        str(raw),
    )
    if match:
        return (
            int(match.group(1)),
            float(match.group(2)),
            float(match.group(3)),
            float(match.group(4)),
        )
    return None


# ============================================================
# 机器人操作封装 (参考 aubo_move.py / startup.py)
# ============================================================
# 注意: 此处重新实现运动函数而非直接 import aubo_move，因为
# aubo_move.py 的 move_relative_l() 存在 bug —— 引用的是
# 模块级 robot_rpc_client 而非传入的参数。

def _get_robot_name(rpc):
    return rpc.getRobotNames()[0]


def _get_robot_interface(rpc):
    return rpc.getRobotInterface(_get_robot_name(rpc))

def wait_robot_arrival(robot_interface):
    """阻塞等待机械臂当前运动完成，返回 0=成功, -1=超时"""
    max_retry = 5
    cnt = 0
    exec_id = robot_interface.getMotionControl().getExecId()
    while exec_id == -1:
        if cnt > max_retry:
            return -1
        time.sleep(0.05)
        cnt += 1
        exec_id = robot_interface.getMotionControl().getExecId()
    while robot_interface.getMotionControl().getExecId() != -1:
        time.sleep(0.05)
    return 0


def robot_init():
    """
    连接机器人 → 登录 → 上电 → 等待就绪。
    返回 (rpc_client, robot_name, robot_interface)
    """
    rpc = pyaubo_sdk.RpcClient()
    rpc.setRequestTimeout(1000)
    rpc.connect(ROBOT_IP, ROBOT_PORT)

    if not rpc.hasConnected():
        raise ConnectionError("❌ RPC 连接失败!")
    print("✅ RPC 连接成功")

    rpc.login(ROBOT_USER, ROBOT_PASSWORD)
    if not rpc.hasLogined():
        raise PermissionError("❌ 机械臂登录失败!")
    print("✅ 机械臂登录成功")

    robot_name = rpc.getRobotNames()[0]
    robot_interface = rpc.getRobotInterface(robot_name)

    # 上电
    ret = robot_interface.getRobotManage().poweron()
    if ret != 0:
        raise RuntimeError(f"❌ 上电请求失败, 错误码: {ret}")
    print("⚡ 正在上电...")

    # 启动
    ret = robot_interface.getRobotManage().startup()
    if ret != 0:
        raise RuntimeError(f"❌ 启动请求失败, 错误码: {ret}")
    print("⚡ 正在启动...")

    # 等待 Running 状态
    while True:
        mode = robot_interface.getRobotState().getRobotModeType()
        print(f"   当前模式: {mode.name}")
        if mode == pyaubo_sdk.RobotModeType.Running:
            break
        time.sleep(1)
    print("✅ 机械臂已就绪 (Running)")

    return rpc, robot_name, robot_interface


def robot_cleanup(rpc):
    """断电 → 登出 → 断开 RPC（异常安全）"""
    try:
        ri = _get_robot_interface(rpc)
        ri.getRobotManage().poweroff()
        print("🔌 机械臂已断电")
    except Exception as e:
        print(f"⚠️  断电异常: {e}")
    try:
        rpc.logout()
        rpc.disconnect()
        print("🔌 RPC 已断开")
    except Exception as e:
        print(f"⚠️  断开异常: {e}")


def robot_move_joint(rpc, joint_angles):
    """关节运动到指定关节角 (弧度)。返回 0=成功, -1=失败"""
    ri = _get_robot_interface(rpc)
    ri.getMotionControl().setSpeedFraction(SPEED_FRACTION)
    ri.getRobotConfig().setTcpOffset([0.0] * 6)
    ri.getMotionControl().moveJoint(joint_angles, JOINT_SPEED, JOINT_ACC, 0, 0)
    return wait_robot_arrival(ri)


def robot_move_line_relative(rpc, offset):
    """
    相对直线运动: offset [dx,dy,dz,drx,dry,drz] 加到当前 tool_pose。

    offset 中位置单位: 米, 姿态单位: 弧度
    返回 0=成功, -1=失败
    """
    ri = _get_robot_interface(rpc)
    ri.getMotionControl().setSpeedFraction(SPEED_FRACTION)
    ri.getRobotConfig().setTcpOffset([0.0] * 6)

    tool_pose = ri.getRobotState().getToolPose()
    target = [a + b for a, b in zip(offset, tool_pose)]
    ri.getMotionControl().moveLine(target, LINEAR_SPEED, LINEAR_ACC, 0, 0)
    return wait_robot_arrival(ri)


def robot_get_tool_pose(rpc):
    """获取当前 TCP 位姿 [x,y,z,rx,ry,rz]"""
    return _get_robot_interface(rpc).getRobotState().getToolPose()


# ============================================================
# 任务执行
# ============================================================

def execute_pick(rpc, color):
    """
    执行一次抓取操作:
    1. 视觉定位目标方块
    2. 水平移动到方块正上方
    3. 下降至抓取高度
    4. 夹爪闭合
    5. 升回安全高度
    """
    print(f"\n  🔍 [PICK] 目标颜色: {color}")

    # 1. 视觉定位
    raw = hikvision.find("pick", color)
    result = parse_find_result(raw)
    if result is None:
        print(f"     ❌ 视觉定位失败, raw={raw}")
        return False
    label, dx, dy, drz = result
    print(f"     📷 视觉结果: label={label}, dx={dx:.4f}m, dy={dy:.4f}m, drz={drz:.2f}°")

    # 2. 水平移动 + 旋转对准 (保持当前 Z 不变)
    ret = robot_move_line_relative(rpc, [dx, dy, 0, 0, 0, math.radians(drz)])
    if ret != 0:
        print("     ❌ 水平移动失败")
        return False
    print("     ✅ 已对准目标上方")

    # 3. 下降至抓取高度
    ret = robot_move_line_relative(rpc, [0, 0, -PICK_DESCENT, 0, 0, 0])
    if ret != 0:
        print("     ❌ 下降失败")
        return False
    print("     ✅ 已下降至抓取高度")

    # 4. 夹爪闭合 (占位)
    print("     🖐️  gripper closed")
    time.sleep(0.5)

    # 5. 升回安全高度
    ret = robot_move_line_relative(rpc, [0, 0, PICK_DESCENT, 0, 0, 0])
    if ret != 0:
        print("     ❌ 抓取后上升失败")
        return False

    print(f"  ✅ [PICK] {color} 方块抓取完成")
    return True


def execute_place(rpc, color):
    """
    执行一次放置操作:
    1. 视觉定位目标盘子
    2. 水平移动到盘子正上方
    3. 下降至放置高度
    4. 夹爪释放
    5. 升回安全高度
    """
    print(f"\n  📍 [PLACE] 目标盘子颜色: {color}")

    # 1. 视觉定位盘子
    raw = hikvision.find("place", color)
    result = parse_find_result(raw)
    if result is None:
        print(f"     ❌ 视觉定位失败, raw={raw}")
        return False
    label, dx, dy, drz = result
    print(f"     📷 视觉结果: label={label}, dx={dx:.4f}m, dy={dy:.4f}m, drz={drz:.2f}°")

    # 2. 水平移动 + 旋转对准
    ret = robot_move_line_relative(rpc, [dx, dy, 0, 0, 0, math.radians(drz)])
    if ret != 0:
        print("     ❌ 水平移动失败")
        return False
    print("     ✅ 已对准盘子正上方")

    # 3. 下降至放置高度
    ret = robot_move_line_relative(rpc, [0, 0, -PLACE_DESCENT, 0, 0, 0])
    if ret != 0:
        print("     ❌ 下降失败")
        return False
    print("     ✅ 已下降至放置高度")

    # 4. 夹爪释放 (占位)
    print("     🖐️  gripper opened")
    time.sleep(0.5)

    # 5. 升回安全高度
    ret = robot_move_line_relative(rpc, [0, 0, PLACE_DESCENT, 0, 0, 0])
    if ret != 0:
        print("     ❌ 放置后上升失败")
        return False

    print(f"  ✅ [PLACE] 放入 {color} 盘完成")
    return True


# ============================================================
# 主流程
# ============================================================

def main():
    print("=" * 60)
    print("  机械臂抓取放置任务 (Pick & Place)")
    print("=" * 60)

    # ---- Phase 1: 生成任务 JSON ----
    file_name = f"workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    print(f"\n{'─' * 40}")
    print(f"[Phase 1] 生成任务编排 JSON → {file_name}")

    prompt.generate_workflow_json(TASK_REQUEST, file_name)
    with open(file_name, 'r', encoding='utf-8') as f:
        task = json.load(f)

    sequence = task.get("assembly_sequence", [])
    print(f"  任务描述: {task.get('task_description', '')}")
    print(f"  共 {len(sequence)} 步")

    # ---- Phase 2: 连接机器人 ----
    print(f"\n{'─' * 40}")
    print("[Phase 2] 连接机器人...")

    rpc = None
    try:
        rpc, robot_name, robot_interface = robot_init()
    except Exception as e:
        print(f"  {e}")
        print("  机器人连接失败，任务终止!")
        return

    try:
        # ---- Phase 3: 执行任务 ----
        print(f"\n{'─' * 40}")
        print("[Phase 3] 开始执行任务序列")

        # 先运动到初始安全位置
        print("\n  🏠 移动到初始关节位置...")
        ret = robot_move_joint(rpc, INIT_JOINT)
        if ret != 0:
            print("  ❌ 关节运动到初始位置失败!")
            return
        print("  ✅ 已到达初始位置 (安全高度)")

        # 遍历任务序列
        failed = False
        for item in sequence:
            step = item["step"]
            operation = item["operation"]
            color = item["object_color"]
            desc = item.get("action_description", "")

            print(f"\n{'─' * 40}")
            print(f"  Step {step}/{len(sequence)}: {desc}")

            if operation == "pick":
                success = execute_pick(rpc, color)
            elif operation == "place":
                success = execute_place(rpc, color)
            else:
                print(f"  ⚠️  未知操作类型: {operation}，跳过")
                continue

            if not success:
                print(f"\n  ❌ 步骤 {step} 执行失败，终止任务!")
                failed = True
                break

        # 回到初始位置
        if not failed:
            print(f"\n{'─' * 40}")
            print("  🏠 返回初始位置...")
            robot_move_joint(rpc, INIT_JOINT)
            print("  ✅ 已返回初始位置")

    finally:
        # ---- Phase 4: 清理 ----
        print(f"\n{'─' * 40}")
        print("[Phase 4] 清理...")
        robot_cleanup(rpc)

    print(f"\n{'=' * 60}")
    print("  所有任务执行完成！")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
