"""Load the original Python 3.12 ForceSensor bytecode from the source project."""

import importlib.util
import os
from pathlib import Path
import sys


_HERE = Path(__file__).resolve().parent
_BYTECODE = _HERE / "legacy" / "force_sensor.cpython-312.pyc"

if sys.version_info[:2] != (3, 12):
    raise RuntimeError("原项目仅保留 Python 3.12 编译版 force_sensor；请使用 Python 3.12")

# The copied ART-DAQ Python package is beside this module and uses absolute imports.
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

_dll_directory = os.add_dll_directory(str(_HERE / "native"))

_spec = importlib.util.spec_from_file_location("_legacy_force_sensor", _BYTECODE)
if _spec is None or _spec.loader is None:
    raise ImportError(f"无法加载原项目的力传感器模块: {_BYTECODE}")
_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_module)
ForceSensor = _module.ForceSensor

__all__ = ["ForceSensor"]
