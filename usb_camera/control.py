"""USB camera snapshot and continuous streaming commands."""

import argparse
from pathlib import Path
import sys
import time

import cv2
from device import select_device, frame_stats


def main():
    parser = argparse.ArgumentParser(description="USB 相机拍摄与取流")
    parser.add_argument("--index", type=int, default=None, help="显式设备索引；Linux 默认按 config.json 匹配外接相机，Windows 必填")
    actions = parser.add_subparsers(dest="action", required=True)
    capture = actions.add_parser("capture", help="拍摄一帧并保存")
    capture.add_argument("--output", type=Path, required=True)
    stream = actions.add_parser("stream", help="连续取流，默认打开预览窗口")
    stream.add_argument("--headless", action="store_true", help="无窗口取流")
    stream.add_argument("--frames", type=int, default=0, help="成功采集帧数；0 为持续取流")
    stream.add_argument("--max-failures", type=int, default=5, help="连续读取失败上限，默认 5")
    args = parser.parse_args()
    if args.index is not None and args.index < 0:
        parser.error("--index 必须大于或等于 0")
    if args.action == "stream":
        if args.frames < 0:
            parser.error("--frames 不能小于 0")
        if args.max_failures <= 0:
            parser.error("--max-failures 必须为正整数")

    source, identity = select_device(args.index)
    print(f"设备: {identity}", flush=True)
    cap = cv2.VideoCapture(source, cv2.CAP_V4L2) if sys.platform.startswith("linux") else cv2.VideoCapture(source)
    window = None
    try:
        if not cap.isOpened():
            raise RuntimeError(f"无法打开 USB 相机索引 {args.index}")
        if args.action == "stream" and not args.headless:
            from preview import Preview
            window = Preview(Path(str(source)).name)
        # Discard startup frames to allow exposure to settle.
        for _ in range(15):
            cap.read()
        count = failures = 0
        start = time.monotonic()
        while True:
            ok, frame = cap.read()
            if not ok or frame is None or frame.size == 0:
                frame = None
                failures += 1
                limit = args.max_failures if args.action == "stream" else 1
                print(f"USB 相机读取失败 ({failures}/{limit})", file=sys.stderr)
                if failures >= limit:
                    raise RuntimeError("USB 相机连续读取失败，请检查连接及设备占用")
                time.sleep(0.05)
            else:
                failures = 0
                count += 1
                if count == 1:
                    suspicious, stats = frame_stats(frame)
                    print(stats, flush=True)
                    if suspicious:
                        print("警告: 画面接近全黑或缺少灰度变化，请检查遮挡、照明和曝光", file=sys.stderr)
                if args.action == "capture":
                    output = args.output.resolve()
                    output.parent.mkdir(parents=True, exist_ok=True)
                    if not cv2.imwrite(str(output), frame):
                        raise RuntimeError(f"保存图像失败: {output}")
                    print(f"saved={output}")
                    break
                if count == 1 or count % 30 == 0:
                    elapsed = max(time.monotonic() - start, 1e-9)
                    print(f"帧 {count}: {frame.shape[1]}x{frame.shape[0]}, 平均 {count / elapsed:.1f} FPS", flush=True)
            if window is not None and not window.update(frame):
                break
            if args.action == "stream" and args.frames and count >= args.frames:
                break
    finally:
        cap.release()
        if window is not None:
            window.close()
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("已停止")
        sys.exit(130)
    except Exception as exc:
        print(f"错误: {exc}", file=sys.stderr)
        sys.exit(1)
