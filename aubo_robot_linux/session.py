"""AUBO connection and raw state access; never powers on or starts the robot."""
import math
import time


class RobotSession:
    def __init__(self, config, sdk=None):
        if sdk is None:
            from sdk_loader import load_sdk
            sdk = load_sdk()
        self.client = sdk.RpcClient()
        self.config = config

    def __enter__(self):
        password = '123456'
        try:
            self.client.setRequestTimeout(3000)
            self.client.connect(self.config['ip'], self.config['port'])
            if not self.client.hasConnected(): raise ConnectionError('AUBO RPC connection failed')
            self.client.login(self.config['user'], password)
            if not self.client.hasLogined(): raise PermissionError('AUBO login failed')
            names = self.client.getRobotNames()
            name = self.config.get('name')
            if name is None:
                if len(names) != 1: raise ValueError('Set robot.name when controller does not expose exactly one robot')
                name = names[0]
            if name not in names: raise ValueError('Configured robot name not found')
            self.name = name
            self.robot = self.client.getRobotInterface(name)
            return self
        except BaseException:
            self.__exit__(None,None,None)
            raise

    def read(self):
        state = self.robot.getRobotState()
        start = time.time_ns()
        result = {'robot':self.name, 'read_start_unix_ns':start,
                  'joints_rad':list(state.getJointPositions()),
                  'tool_pose_sdk':list(state.getToolPose()),
                  'tcp_pose_sdk':list(state.getTcpPose()),
                  'mode':state.getRobotModeType().name,
                  'safety_mode':state.getSafetyModeType().name}
        for key in ('joints_rad','tool_pose_sdk','tcp_pose_sdk'):
            if len(result[key]) != 6 or not all(math.isfinite(v) for v in result[key]):
                raise ValueError(f'Invalid robot state: {key}')
        result['read_end_unix_ns'] = time.time_ns()
        return result

    def __exit__(self, *exc):
        if self.client.hasConnected():
            try:
                if self.client.hasLogined(): self.client.logout()
            finally: self.client.disconnect()
