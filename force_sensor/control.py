"""Read the three-axis ART-DAQ force sensor from the command line."""

import argparse
import math


def main():
    parser = argparse.ArgumentParser(description="三轴力传感器采集，单位 N")
    parser.add_argument("--sensitivity", type=float, default=20.0, help="灵敏度，N/V；默认 20")
    parser.add_argument("--zero-calib", action="store_true", help="启动时采样 100 次进行零点校准")
    actions = parser.add_subparsers(dest="action", required=True)
    actions.add_parser("once", help="读取一组 Fx/Fy/Fz")
    average = actions.add_parser("average", help="读取 N 组并输出平均值")
    average.add_argument("count", type=int)
    stream = actions.add_parser("stream", help="连续读取；Ctrl+C 退出")
    stream.add_argument("--limit", type=int, help="读取指定组数后退出")
    args = parser.parse_args()
    if not math.isfinite(args.sensitivity) or args.sensitivity <= 0:
        parser.error("--sensitivity 必须为正数")
    if args.action == "average" and args.count <= 0:
        parser.error("count 必须大于 0")
    if args.action == "stream" and args.limit is not None and args.limit <= 0:
        parser.error("--limit 必须大于 0")

    from force_sensor import ForceSensor

    sensor = ForceSensor(sensitivity=args.sensitivity, zero_calib=args.zero_calib)
    try:
        if args.action == "once":
            fx, fy, fz = sensor.read_one()
            print(f"Fx={fx:.3f} N  Fy={fy:.3f} N  Fz={fz:.3f} N")
        elif args.action == "average":
            import numpy as np

            axes = sensor.read_n(args.count)
            fx, fy, fz = (float(np.mean(axis)) for axis in axes)
            print(f"N={args.count}  Fx={fx:.3f} N  Fy={fy:.3f} N  Fz={fz:.3f} N")
        else:
            try:
                for index, (fx, fy, fz) in enumerate(sensor.read_continuous(), start=1):
                    print(f"{index}: Fx={fx:.3f} N  Fy={fy:.3f} N  Fz={fz:.3f} N")
                    if args.limit is not None and index >= args.limit:
                        break
            except KeyboardInterrupt:
                print("采集已停止")
    finally:
        sensor.close()


if __name__ == "__main__":
    main()
