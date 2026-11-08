from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import ctypes

from artdaq._lib import (
    lib_importer, ctypes_byte_str)
from artdaq.errors import (check_for_error, is_string_buffer_too_small)
from artdaq._task_modules.channels.channel import Channel
from artdaq.constants import (AOOutputChannelType, _TermCfg)

class AOChannel(Channel):
    """
    Represents one or more analog output virtual channels and their properties.
    """
    __slots__ = []

    def __repr__(self):
        return 'AOChannel(name={0})'.format(self._name)

    @property
    def ao_max(self):
        """
        str: Specifies the maximum value you expect to generate.
        The value is in the units you specify with a units property.
        If you try to write a value larger than the maximum value,
        ArtDAQ generates an error. ArtDAQ might coerce this value
        to a smaller value if other task settings restrict the device
        from generating the desired maximum.
        """
        val = ctypes.c_double()
        cfunc = lib_importer.windll.ArtDAQ_GetAOMax
        if cfunc.argtypes is None:
            with cfunc.arglock:
                if cfunc.argtypes is None:
                    cfunc.argtypes = [
                        lib_importer.task_handle, ctypes_byte_str, ctypes.POINTER(ctypes.c_double)]

        error_code = cfunc(self._handle, self._name, ctypes.byref(val))
        check_for_error(error_code)
        return val.value

    @ao_max.setter
    def ao_max(self, val):
        cfunc = lib_importer.windll.ArtDAQ_SetAOMax
        if cfunc.argtypes is None:
            with cfunc.arglock:
                if cfunc.argtypes is None:
                    cfunc.argtypes = [
                        lib_importer.task_handle, ctypes_byte_str, ctypes.c_double]

        error_code = cfunc(
            self._handle, self._name, val)
        check_for_error(error_code)

    @ao_max.deleter
    def ao_max(self):
        cfunc = lib_importer.windll.ArtDAQ_ResetAOMax
        if cfunc.argtypes is None:
            with cfunc.arglock:
                if cfunc.argtypes is None:
                    cfunc.argtypes = [
                        lib_importer.task_handle, ctypes_byte_str]

        error_code = cfunc(self._handle, self._name)
        check_for_error(error_code)

    @property
    def ao_min(self):
        """
        str: Specifies the minimum value you expect to generate.
        The value is in the units you specify with a units property.
        If you try to write a value smaller than the minimum value,
        ArtDAQ generates an error. ArtDAQ might coerce this value to
        a larger value if other task settings restrict the device
        from generating the desired minimum.
        """
        val = ctypes.c_double()
        cfunc = lib_importer.windll.ArtDAQ_GetAOMin
        if cfunc.argtypes is None:
            with cfunc.arglock:
                if cfunc.argtypes is None:
                    cfunc.argtypes = [
                        lib_importer.task_handle, ctypes_byte_str, ctypes.POINTER(ctypes.c_double)]

        error_code = cfunc(self._handle, self._name, ctypes.byref(val))
        check_for_error(error_code)
        return val.value

    @ao_min.setter
    def ao_min(self, val):
        cfunc = lib_importer.windll.ArtDAQ_SetAOMin
        if cfunc.argtypes is None:
            with cfunc.arglock:
                if cfunc.argtypes is None:
                    cfunc.argtypes = [
                        lib_importer.task_handle, ctypes_byte_str, ctypes.c_double]

        error_code = cfunc(
            self._handle, self._name, val)
        check_for_error(error_code)

    @ao_min.deleter
    def ao_min(self):
        cfunc = lib_importer.windll.ArtDAQ_ResetAOMin
        if cfunc.argtypes is None:
            with cfunc.arglock:
                if cfunc.argtypes is None:
                    cfunc.argtypes = [
                        lib_importer.task_handle, ctypes_byte_str]

        error_code = cfunc(self._handle, self._name)
        check_for_error(error_code)

    @property
    def ao_customscalename(self):
        """
        str: Specifies the name of a custom scale for the channel.
        """

        cfunc = lib_importer.windll.ArtDAQ_GetAOCustomScaleName
        if cfunc.argtypes is None:
            with cfunc.arglock:
                if cfunc.argtypes is None:
                    cfunc.argtypes = [
                        lib_importer.task_handle, ctypes_byte_str, ctypes.c_char_p, ctypes.c_uint]

        temp_size = 256
        while True:
            val = ctypes.create_string_buffer(temp_size)

            size_or_code = cfunc(
                self._handle, self._name, val, temp_size)

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

    @ao_customscalename.setter
    def ao_customscalename(self, val):
        cfunc = lib_importer.windll.ArtDAQ_SetAOCustomScaleName
        if cfunc.argtypes is None:
            with cfunc.arglock:
                if cfunc.argtypes is None:
                    cfunc.argtypes = [
                        lib_importer.task_handle, ctypes_byte_str, ctypes_byte_str]

        error_code = cfunc(
            self._handle, self._name, val)
        check_for_error(error_code)

    @ao_customscalename.deleter
    def ao_customscalename(self):
        cfunc = lib_importer.windll.ArtDAQ_ResetAOCustomScaleName
        if cfunc.argtypes is None:
            with cfunc.arglock:
                if cfunc.argtypes is None:
                    cfunc.argtypes = [
                        lib_importer.task_handle, ctypes_byte_str]

        error_code = cfunc(self)
        check_for_error(error_code)

    @property
    def ao_outputtype(self):
        """
        str: Indicates whether the channel generates voltage,  current, or a waveform.
        """
        val = ctypes.c_int32()
        cfunc = lib_importer.windll.ArtDAQ_GetAOOutputType
        if cfunc.argtypes is None:
            with cfunc.arglock:
                if cfunc.argtypes is None:
                    cfunc.argtypes = [
                        lib_importer.task_handle, ctypes_byte_str, ctypes.POINTER(ctypes.c_int32)]

        error_code = cfunc(self._handle, self._name, ctypes.byref(val))
        check_for_error(error_code)
        return AOOutputChannelType(val.value)

    @property
    def ao_termcfg(self):
        val = ctypes.c_int32
        cfunc = lib_importer.windll.ArtDAQ_GetAOTermCfg
        if cfunc.argtypes is None:
            with cfunc.arglock:
                cfunc.argtypes = [self._handle, ctypes_byte_str, ctypes.POINTER(ctypes.c_int32)]
        error_code = cfunc(self._handle, self._name, ctypes.byref(val))
        check_for_error(error_code)
        return _TermCfg(val.value)

    @ ao_termcfg.setter
    def ao_termcfg(self, val):
        cfunc = lib_importer.windll.ArtDAQ_SetAOTermCfg
        if cfunc.argtypes is None:
            with cfunc.arglock:
                cfunc.argtypes = [self._handle, ctypes_byte_str, ctypes.c_int32]
        error_code = cfunc(self._handle, self._name, val)
        check_for_error(error_code)

    @ao_termcfg.deleter
    def ao_termcfg(self, val):
        cfunc = lib_importer.windll.ArtDAQ_ResetAOTermCfg
        if cfunc.argtypes is None:
            with cfunc.arglock:
                cfunc.argtypes = [self._handle, ctypes_byte_str]
        error_code = cfunc(self._handle, self._name)
        check_for_error(error_code)














































































