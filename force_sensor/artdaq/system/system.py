from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import collections
import ctypes
import numpy

from artdaq._lib import (
    lib_importer, wrapped_ndpointer, enum_bitfield_to_list, ctypes_byte_str,
    c_bool32)
from artdaq.errors import check_for_error, is_string_buffer_too_small
from artdaq.system.device import Device

__all__ = ['System']


class System(object):
    """
    Represents a Artdaq system.

    Contains static properties that access tasks, scales, and global channels
    stored in DMC, performs immediate
    operations on DAQ hardware, and creates classes from which you can get
    information about the hardware.
    """
    @staticmethod
    def local():
      return System()

    def tasks():
        """
                str: Indicates the name of the tasks.
                """
        cfunc = lib_importer.windll.ArtDAQ_GetSystemAttribute
        if cfunc.argtypes is None:
            with cfunc.arglock:
                if cfunc.argtypes is None:
                    cfunc.argtypes = [ctypes.c_uint, ctypes.c_char_p,
                        ctypes.c_int]

        temp_size = 256
        while True:
            val = ctypes.create_string_buffer(temp_size)
            size_or_code = cfunc(
                0x1267, val, temp_size)

            if is_string_buffer_too_small(size_or_code):
                # Buffer size must have changed between calls; check again.
                temp_size = 0
            elif size_or_code > 0 and temp_size == 0:
                # Buffer size obtained, use to retrieve data.
                temp_size = size_or_code
            else:
                break

        check_for_error(size_or_code)

        return val.value.decode('ascii')

    def device_name():
        """
                str: Indicates the name of the tasks.
                """
        cfunc = lib_importer.windll.ArtDAQ_GetSystemAttribute
        if cfunc.argtypes is None:
            with cfunc.arglock:
                if cfunc.argtypes is None:
                    cfunc.argtypes = [ctypes.c_uint, ctypes.c_char_p,
                        ctypes.c_int]

        temp_size = 256
        while True:
            val = ctypes.create_string_buffer(temp_size)
            size_or_code = cfunc(0x193B, val, temp_size)

            if is_string_buffer_too_small(size_or_code):
                # Buffer size must have changed between calls; check again.
                temp_size = 0
            elif size_or_code > 0 and temp_size == 0:
                # Buffer size obtained, use to retrieve data.
                temp_size = size_or_code
            else:
                break

        check_for_error(size_or_code)

        return val.value.decode('ascii')


    # endregion
