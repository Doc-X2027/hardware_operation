# main.py
# 导纳控制主程序

import time
import signal
import sys
import numpy as np
from typing import Optional

import config
from force_sensor import ForceSensor
from aubo_robot import AuboRobot
from admittance_controller import AdmittanceController


class AdmittanceControlSystem:
    """
    导纳控制系统主类
    整合力传感器、导纳控制器、机械臂
    """
    
    def __init__(self):
        # 加载配置
        self.dt = config.CONTROL_DT
        
        # 力传感器（已包含零点校准）
        self.sensor = ForceSensor(zero_calib=True)
        
        # 机械臂接口
        self.robot = AuboRobot(
            ip=config.ROBOT_IP,
            port=config.ROBOT_PORT,
            username=config.ROBOT_USER,
            password=config.ROBOT_PASSWORD
        )
        
        # 导纳控制器
        self.admittance_ctrl = AdmittanceController(
            md=config.ADMITTANCE_PARAMS["Md"],
            bd=config.ADMITTANCE_PARAMS["Bd"],
            kd=config.ADMITTANCE_PARAMS["Kd"],
            dt=self.dt
        )
        
        # 设置期望力
        self.admittance_ctrl.set_desired_force(
            config.DESIRED_FORCE[0],
            config.DESIRED_FORCE[1],
            config.DESIRED_FORCE[2]
        )
        
        # 控制标志
        self.is_running = False
        
        # 安全保护
        self.max_force = config.MAX_FORCE
        
        # 目标位姿
        self.initial_pose = None
        self.target_pose = None
        
        # 信号处理
        signal.signal(signal.SIGINT, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """处理Ctrl+C信号"""
        print("\n收到中断信号，正在停止...")
        self.stop()
        sys.exit(0)
    
        # 获取初始位姿
        self.initial_pose = self.robot.get_current_pose()
        self.target_pose = self.initial_pose.copy()
        print(f"初始位姿: x={self.initial_pose[0]:.3f}, y={self.initial_pose[1]:.3f}, "
              f"z={self.initial_pose[2]:.3f}")
        
        # 设置速度比率
        self.robot.set_speed_fraction(0.5)
        
        # 2. 验证力传感器（零点校准已在初始化时完成）
        print("\n[2/4] 验证力传感器...")
        fx, fy, fz = self.sensor.read_one()
        print(f"当前力读数: Fx={fx:+.2f}N, Fy={fy:+.2f}N, Fz={fz:+.2f}N")
        print("说明: 零点校准已完成，当前读数为接触力(已消除工具重力偏置)")
        
        # 3. 初始化导纳控制器
        print("\n[3/4] 初始化导纳控制器...")
        self.admittance_ctrl.reset()
        self.admittance_ctrl.set_desired_force(
            config.DESIRED_FORCE[0],
            config.DESIRED_FORCE[1],
            config.DESIRED_FORCE[2]
        )
        print(f"期望接触力: Fx={config.DESIRED_FORCE[0]:.1f}N, "
              f"Fy={config.DESIRED_FORCE[1]:.1f}N, Fz={config.DESIRED_FORCE[2]:.1f}N")
        
        # 4. 安全确认
        print("\n[4/4] 安全检查...")
        print(f"最大接触力保护阈值: {self.max_force}N")
        print(f"最大位置修正量: {config.MAX_POSITION_CORRECTION * 1000:.1f}mm")
        
        print("\n" + "=" * 60)
        print("初始化完成!")
        print("=" * 60)
        
        return True
    
    def force_protection_check(self, fx: float, fy: float, fz: float) -> bool:
        """力保护检查"""
        if abs(fx) > self.max_force or abs(fy) > self.max_force or abs(fz) > self.max_force:
            print(f"\n!!! 警告: 接触力超过保护阈值 !!!")
            print(f"当前力: ({fx:.1f}, {fy:.1f}, {fz:.1f})N")
            return False
        return True
    
    def move_to_start_position(self) -> bool:
        """移动到起始位置"""
        print("\n移动到起始位置...")
        
        # 定义一个安全的起始位姿（根据实际场景调整）
        start_pose = self.initial_pose.copy()
        
        # 如果当前姿态过于接近，先抬升Z轴
        current_z = self.robot.get_current_pose()[2]
        if abs(current_z - start_pose[2]) < 0.05:
            start_pose[2] += 0.1  # 先抬高10cm
        
        return self.robot.move_pose(start_pose, speed=0.2, acc=0.1)
    
    def run_admittance_control(self, duration: Optional[float] = None,
                               use_deadzone: bool = False,
                               deadzone: float = 1.0):
        """
        运行导纳控制
        
        Args:
            duration: 运行时间(秒)，None表示无限运行直到Ctrl+C
            use_deadzone: 是否使用死区
            deadzone: 死区阈值(N)
        """
        print("\n" + "=" * 60)
        print("开始导纳控制模式")
        print("=" * 60)
        print("注意: 旋转自由度已锁死，仅平移自由度响应")
        print("按 Ctrl+C 停止控制")
        
        self.is_running = True
        start_time = time.time()
        loop_count = 0
        
        # 获取当前位姿作为目标
        self.target_pose = self.robot.get_current_pose()
        
        # 重置控制器
        self.admittance_ctrl.reset()
        
        try:
            while self.is_running:
                loop_start = time.time()
                
                # 检查运行时间
                if duration and (time.time() - start_time) > duration:
                    print(f"\n运行时间({duration}s)已到，停止控制")
                    break
                
                # 1. 读取力数据（已自动进行零点校准）
                fx, fy, fz = self.sensor.read_one()
                
                # 2. 安全保护检查
                if not self.force_protection_check(fx, fy, fz):
                    self.robot.stop()
                    break
                
                # 3. 计算位置修正量
                if use_deadzone:
                    correction = self.admittance_ctrl.compute_correction_with_deadzone(
                        (fx, fy, fz), deadzone
                    )
                else:
                    correction = self.admittance_ctrl.compute_correction((fx, fy, fz))
                
                # 4. 限制修正量
                correction = np.clip(correction, 
                                   -config.MAX_POSITION_CORRECTION, 
                                   config.MAX_POSITION_CORRECTION)
                
                # 5. 计算修正后的目标位姿
                corrected_pose = self.target_pose.copy()
                corrected_pose[0] += correction[0]
                corrected_pose[1] += correction[1]
                corrected_pose[2] += correction[2]
                # 姿态保持不变
                
                # 6. 发送指令（非阻塞，使用较快的速度）
                self.robot.move_line(corrected_pose, 
                                    speed=config.MOVE_SPEED,
                                    acc=config.MOVE_ACC,
                                    wait=False)
                
                # 7. 调试输出
                if config.DEBUG_MODE and loop_count % 50 == 0:
                    print(f"\n[循环 {loop_count}]")
                    print(f"  测量力: Fx={fx:+6.2f}N, Fy={fy:+6.2f}N, Fz={fz:+6.2f}N")
                    print(f"  修正量: dx={correction[0]*1000:+6.2f}mm, "
                          f"dy={correction[1]*1000:+6.2f}mm, dz={correction[2]*1000:+6.2f}mm")
                    print(f"  目标位姿: x={corrected_pose[0]:+.3f}, "
                          f"y={corrected_pose[1]:+.3f}, z={corrected_pose[2]:+.3f}")
                
                # 8. 控制频率保持
                elapsed = time.time() - loop_start
                sleep_time = self.dt - elapsed
                if sleep_time > 0:
                    time.sleep(sleep_time)
                
                loop_count += 1
                
        except KeyboardInterrupt:
            print("\n用户中断")
        except Exception as e:
            print(f"\n控制循环异常: {e}")
        finally:
            self.is_running = False
            self.robot.stop()
            print("\n导纳控制已停止")
    
    def run_zero_force_drag(self, duration: Optional[float] = None):
        """
        零力拖动模式
        使用低阻尼、低刚度的导纳控制实现力觉拖动
        
        Args:
            duration: 运行时间(秒)
        """
        print("\n" + "=" * 60)
        print("进入零力拖动模式")
        print("=" * 60)
        print("请手动拖动机械臂末端")
        print("按 Ctrl+C 退出")
        
        # 保存原始参数
        original_bd = config.ADMITTANCE_PARAMS["Bd"].copy()
        original_kd = config.ADMITTANCE_PARAMS["Kd"].copy()
        
        # 设置低阻尼、低刚度（更易拖动）
        self.admittance_ctrl.set_damping([10.0, 10.0, 20.0])   # 低阻尼
        self.admittance_ctrl.set_stiffness([50.0, 50.0, 100.0])  # 低刚度
        self.admittance_ctrl.set_desired_force(0, 0, 0)  # 期望力为0
        
        # 运行导纳控制
        self.run_admittance_control(duration=duration, use_deadzone=True, deadzone=0.5)
        
        # 恢复原始参数
        self.admittance_ctrl.set_damping(original_bd)
        self.admittance_ctrl.set_stiffness(original_kd)
        self.admittance_ctrl.set_desired_force(
            config.DESIRED_FORCE[0],
            config.DESIRED_FORCE[1],
            config.DESIRED_FORCE[2]
        )
    
    def run_constant_force(self, force_z: float = 10.0, 
                           approach_distance: float = 0.02,
                           duration: float = 30.0):
        """
        恒力控制模式（如打磨、抛光）
        
        Args:
            force_z: Z方向期望力(N)
            approach_distance: 接近距离(m)
            duration: 持续时间(s)
        """
        print("\n" + "=" * 60)
        print(f"恒力控制模式 - 期望力 Z: {force_z}N")
        print("=" * 60)
        
        # 设置期望力（仅Z方向）
        self.admittance_ctrl.set_desired_force(0, 0, force_z)
        
        # 先缓慢接近接触面
        print("缓慢接近接触面...")
        current_pose = self.robot.get_current_pose()
        approach_pose = current_pose.copy()
        approach_pose[2] -= approach_distance  # 向下移动
        
        self.robot.move_line(approach_pose, speed=0.05, acc=0.05)
        
        # 运行导纳控制
        self.run_admittance_control(duration=duration, use_deadzone=True, deadzone=0.5)
        
        # 恢复
        self.admittance_ctrl.set_desired_force(
            config.DESIRED_FORCE[0],
            config.DESIRED_FORCE[1],
            config.DESIRED_FORCE[2]
        )
    
    def stop(self):
        """停止控制系统"""
        self.is_running = False
        if self.robot:
            self.robot.stop()
    
    def cleanup(self):
        """清理资源"""
        print("\n清理资源...")
        self.stop()
        if self.robot:
            self.robot.disconnect()
        if self.sensor:
            self.sensor.close()
        print("清理完成")


def main():
    """主函数"""
    system = AdmittanceControlSystem()
        
    # 移动到一个安全起始位置
    system.move_to_start_position()
    
    # 显示菜单
    print("\n请选择运行模式:")
    print("1. 标准导纳控制")
    print("2. 零力拖动模式")
    print("3. 恒力控制模式(Z方向)")
    print("4. 退出")
    
    choice = input("\n请输入选择 (1-4): ").strip()
    
    if choice == "1":
        system.run_admittance_control(duration=60, use_deadzone=True)
    elif choice == "2":
        system.run_zero_force_drag(duration=60)
    elif choice == "3":
        force = float(input("请输入期望力(N)[默认10]: ") or "10")
        system.run_constant_force(force_z=force, duration=60)
    else:
        print("退出")

        system.cleanup()


if __name__ == "__main__":
    main()