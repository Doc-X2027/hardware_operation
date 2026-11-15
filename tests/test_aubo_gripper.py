import unittest
from unittest.mock import Mock

from aubo_robot_linux.gripper import control_gripper, main


class GripperTests(unittest.TestCase):
    def register(self):
        return Mock(**{
            'modbusGetSignalNames.return_value': ['Modbus_0'],
            'modbusGetSignalTypes.return_value': [3],
            'modbusGetSignalError.return_value': 0,
            'modbusGetSignalStatus.return_value': 1000,
            'modbusSetOutputSignal.return_value': 0,
        })

    def test_commands(self):
        for action, value in [('grip', 0), ('release', 1000)]:
            with self.subTest(action=action):
                register = self.register()
                control_gripper(register, 'Modbus_0', action)
                register.modbusSetOutputSignal.assert_called_once_with('Modbus_0', value)

    def test_status_does_not_write(self):
        register = self.register()
        control_gripper(register, 'Modbus_0', 'status')
        register.modbusSetOutputSignal.assert_not_called()

    def test_invalid_signal_does_not_write(self):
        for method, value in [('modbusGetSignalNames', []),
                              ('modbusGetSignalTypes', [1]),
                              ('modbusGetSignalTypes', []),
                              ('modbusGetSignalError', 6)]:
            with self.subTest(method=method, value=value):
                register = self.register()
                getattr(register, method).return_value = value
                with self.assertRaises(RuntimeError):
                    control_gripper(register, 'Modbus_0', 'grip')
                register.modbusSetOutputSignal.assert_not_called()

    def test_write_failure_disconnects_without_retry(self):
        register = self.register()
        register.modbusSetOutputSignal.return_value = -1
        sdk = Mock()
        client = sdk.RpcClient.return_value
        client.getRegisterControl.return_value = register
        with self.assertRaises(RuntimeError):
            main(['--password', 'test-password', 'grip'], sdk=sdk)
        client.login.assert_called_once_with('aubo', 'test-password')
        register.modbusSetOutputSignal.assert_called_once()
        client.logout.assert_called_once()
        client.disconnect.assert_called_once()


if __name__ == '__main__':
    unittest.main()
