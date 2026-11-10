"""Self-check regression tests; no physical device access."""
import contextlib
import io
import json
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import self_check as sc


class SelfCheckTests(unittest.TestCase):
    def test_sdk_noise_does_not_corrupt_result(self):
        output = 'SDK log\nSELF_CHECK_RESULT={"status":"PASS","detail":"frame"}\nshutdown log'
        process = subprocess.CompletedProcess([], 0, output, 'native warning')
        with patch.object(sc.subprocess, 'run', return_value=process):
            check = sc.isolated_probe('USB', ['worker'], 1, structured=True)
        self.assertEqual(check, sc.result('USB', 'PASS', 'frame'))

    def test_crash_timeout_and_malformed_results_fail(self):
        for process in (subprocess.CompletedProcess([], -11, '', 'segfault'),
                        subprocess.CompletedProcess([], 0, 'no result', ''),
                        subprocess.CompletedProcess([], 0, 'SELF_CHECK_RESULT={}', '')):
            with self.subTest(process=process), patch.object(sc.subprocess, 'run', return_value=process):
                self.assertEqual(sc.isolated_probe('USB', ['worker'], 1, structured=True)['status'], 'FAIL')
        with patch.object(sc.subprocess, 'run', side_effect=subprocess.TimeoutExpired('worker', 1)):
            self.assertEqual(sc.isolated_probe('USB', ['worker'], 1)['status'], 'FAIL')

    def test_restore_failure_is_not_pass(self):
        process = subprocess.CompletedProcess([], 0, '帧 1', '恢复 TriggerMode 失败: device lost')
        with patch.object(sc.subprocess, 'run', return_value=process):
            self.assertEqual(sc.isolated_probe('GigE', ['stream'], 1)['status'], 'FAIL')

    def test_offline_never_probes_hardware(self):
        output = io.StringIO()
        with patch.object(sys, 'argv', ['self_check.py', '--offline', '--json']), \
             patch.object(sc, 'isolated_probe', return_value=sc.result('依赖', 'PASS', 'ok')) as isolated, \
             patch.object(sc, 'tcp_probe', side_effect=AssertionError('network accessed')), \
             patch.object(sc, 'force_probe', side_effect=AssertionError('force accessed')), \
             contextlib.redirect_stdout(output):
            self.assertEqual(sc.main(), 0)
        checks = json.loads(output.getvalue())
        self.assertTrue(any(c['item'] == 'GigE 相机' and c['status'] == 'SKIP' for c in checks))
        for call in isolated.call_args_list:
            command = call.args[1]
            self.assertIn('--worker', command)
            self.assertIn(command[command.index('--worker') + 1], ('opencv', 'aravis-deps', 'mvs-deps'))

    def test_multiple_usb_indices_are_deduplicated(self):
        argv = ['self_check.py', '--skip-robot', '--skip-gige', '--skip-force', '--usb-index', '0', '4', '0', '--json']
        with patch.object(sys, 'argv', argv), \
             patch.object(sc, 'isolated_probe', side_effect=lambda name, *a, **kw: sc.result(name, 'PASS', 'mock')) as probe, \
             contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(sc.main(), 0)
        self.assertEqual([call.args[0] for call in probe.call_args_list], ['USB 依赖', 'USB 相机 [0]', 'USB 相机 [4]'])

    def test_invalid_arguments_exit_two(self):
        for args in (['--timeout', 'nan'], ['--timeout', 'inf'], ['--timeout', '0'],
                     ['--robot-port', '65536'], ['--socket-port', '0'], ['--usb-index', '-1']):
            with self.subTest(args=args), patch.object(sys, 'argv', ['self_check.py', *args]), \
                 contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as exc:
                sc.main()
            self.assertEqual(exc.exception.code, 2)


if __name__ == '__main__':
    unittest.main()
