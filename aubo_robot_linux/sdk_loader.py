"""Load the bundled Linux CPython 3.12 SDK."""
from pathlib import Path
import sys


def load_sdk():
    sys.path.insert(0, str(Path(__file__).resolve().parent / 'lib'))
    try:
        import pyaubo_sdk
    except ImportError as exc:
        raise RuntimeError('SDK 需要 Linux x86_64 / Python 3.12；请使用 ./run.sh') from exc
    return pyaubo_sdk
