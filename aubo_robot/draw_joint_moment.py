import matplotlib.pyplot as plt
import numpy as np
from collections import deque
import time
import matplotlib
matplotlib.use('TkAgg')

# 设置中文字体，解决乱码问题
matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'KaiTi']
# 解决负号显示异常的问题
matplotlib.rcParams['axes.unicode_minus'] = False

def realtime_plot(data_source_func, max_points=1000, update_interval=0.1):
    """
    实时绘制持续更新的变量

    参数:
        data_source_func: 可调用对象，每次调用返回新的数据点（数值）
        max_points: 图表显示的最大数据点数
        update_interval: 更新间隔（秒）
    """
    plt.ion()  # 开启交互模式
    fig, ax = plt.subplots()

    # 使用双端队列存储数据，自动移除旧数据
    data_queue = deque(maxlen=max_points)

    # 初始化绘图对象
    line, = ax.plot([], [], 'b-', linewidth=2)
    ax.set_xlim(0, max_points)
    ax.set_ylim(0, 10)  # 可根据实际情况调整
    ax.set_xlabel('时间点')
    ax.set_ylabel('变量值')
    ax.set_title('实时数据监控')
    ax.grid(True)

    try:
        while True:
            # 获取新数据
            new_value = data_source_func()
            data_queue.append(new_value)

            # 更新图形数据
            x_data = list(range(len(data_queue)))
            y_data = list(data_queue)
            line.set_data(x_data, y_data)

            # 动态调整y轴范围（可选）
            if y_data:
                y_min, y_max = min(y_data), max(y_data)
                margin = (y_max - y_min) * 0.1 if y_max != y_min else 1
                ax.set_ylim(y_min - margin, y_max + margin)

            # 调整x轴范围
            if len(data_queue) == max_points:
                ax.set_xlim(len(data_queue) - max_points, len(data_queue))
            else:
                ax.set_xlim(0, max_points)

            # 重绘
            fig.canvas.draw()
            fig.canvas.flush_events()

            time.sleep(update_interval)

    except KeyboardInterrupt:
        print("\n绘图已停止")
    finally:
        plt.ioff()
        plt.show()


# 示例使用：模拟一个持续更新的变量
def demo_data_source():
    """示例数据源：生成随机波动数据"""
    import random
    return random.uniform(0, 10)  # 模拟0-10之间的随机值


if __name__ == "__main__":
    # 运行实时绘图
    realtime_plot(demo_data_source, max_points=50, update_interval=0.2)