"""USB camera snapshot and color detection commands."""

import argparse
from pathlib import Path

import cv2

from shijue import Vision


def main():
    parser = argparse.ArgumentParser(description="USB 相机调用")
    parser.add_argument("--index", type=int, default=0, help="OpenCV 设备索引，默认 0")
    actions = parser.add_subparsers(dest="action", required=True)
    capture = actions.add_parser("capture", help="拍摄一帧")
    capture.add_argument("--output", type=Path, required=True)
    detect = actions.add_parser("detect", help="识别指定颜色物块")
    detect.add_argument("color", choices=("红", "绿", "蓝", "黄", "Red", "Green", "Blue", "Yellow"))
    detect.add_argument("--output", type=Path, help="保存标注后的图像")
    args = parser.parse_args()
    if args.index < 0:
        parser.error("--index 必须大于或等于 0")

    vision = Vision(args.index)
    try:
        if args.action == "capture":
            ok, frame = vision.cap.read()
            if not ok:
                raise RuntimeError("USB 相机读取图像失败")
        else:
            positions, frame = vision.get_block_positions(args.color)
            if frame is None:
                raise RuntimeError("USB 相机读取图像失败")
            print(f"positions_pixels_and_degrees={positions}")
        if args.output:
            output = args.output.resolve()
            if not cv2.imwrite(str(output), frame):
                raise RuntimeError(f"保存图像失败: {output}")
            print(f"saved={output}")
    finally:
        vision.close()


if __name__ == "__main__":
    main()
