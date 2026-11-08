"""Original force sensor usage: zero, single sample, average and streaming."""

import numpy as np

from force_sensor import ForceSensor


def main():
    sensor = ForceSensor(zero_calib=True)
    try:
        fx, fy, fz = sensor.read_one()
        print(f"力: Fx={fx:.2f}N, Fy={fy:.2f}N, Fz={fz:.2f}N")

        fx_list, fy_list, fz_list = sensor.read_n(10)
        print(f"平均力: Fx={np.mean(fx_list):.2f}N")

        def on_force_update(fx, fy, fz):
            print(f"当前力: Fx={fx:.2f}N, Fy={fy:.2f}N, Fz={fz:.2f}N")

        print("开始连续采集（按 Ctrl+C 停止）...")
        for fx, fy, fz in sensor.read_continuous(callback=on_force_update):
            if abs(fx) > 100 or abs(fy) > 100 or abs(fz) > 100:
                print("检测到力超过阈值，停止采集。")
                break
    except KeyboardInterrupt:
        print("采集已停止")
    finally:
        sensor.close()


if __name__ == "__main__":
    main()
