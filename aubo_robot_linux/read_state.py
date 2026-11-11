"""读取机械臂状态，输出 JSON；不执行上电或运动。"""
import argparse
import json
import os
from pathlib import Path
from session import RobotSession


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ip', default=os.getenv('AUBO_IP', '192.168.34.10'))
    parser.add_argument('--port', type=int, default=30004)
    parser.add_argument('--user', default=os.getenv('AUBO_USER', 'aubo'))
    parser.add_argument('--name', default=None)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if args.output and args.output.exists():
        parser.error('输出文件已存在，请选择新路径')
    with RobotSession(vars(args)) as session:
        result = session.read()
    content = json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open('x') as stream:
            stream.write(content + '\n')
    print(content)


if __name__ == '__main__':
    main()
