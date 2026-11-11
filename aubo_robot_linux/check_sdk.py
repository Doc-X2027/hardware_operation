"""仅验证 SDK 导入，不连接机械臂。"""
import sys
from sdk_loader import load_sdk

sdk = load_sdk()
print(f'Python: {sys.version.split()[0]}')
print(f'SDK: {sdk.__file__}')
assert hasattr(sdk, 'RpcClient')
print('SDK 导入成功（未连接机械臂）')
