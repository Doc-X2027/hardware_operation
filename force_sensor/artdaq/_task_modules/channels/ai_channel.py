from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import ctypes

from artdaq._lib import (
    lib_importer, ctypes_byte_str)
from artdaq.errors import (check_for_error, is_string_buffer_too_small)
from artdaq._task_modules.channels.channel import Channel
from artdaq.constants import (AIMeasurementType, InputTermCfg, AutoZeroType,
                              RtdType)



class AIChannel(Channel):
    """
    Represents one or more analog input virtual channels and their properties.
    """
    __slots__ = []

    def __repr__(self):
        return 'AIChannel(name={0})'.format(self._name)

    @property
    def ai_input_src(self):
        """
        str: Specifies the source of the channel. You can use the signal
            from the I/O connector or one of several calibration
            signals. Certain devices have a single calibration signal
            bus. For these devices, you must specify the same
            calibration signal for all channels you connect to a
            calibration signal.
        """
        cfunc = lib_importer.windll.ArtDAQ_GetAIInputSrc
        if cfunc.argtypes is None:
            with cfunc.arglock:
                if cfunc.argtypes is None:
                    cfunc.argtypes = [
                        lib_importer.task_handle, ctypes_byte_str,
                        ctypes.c_char_p, ctypes.c_uint]

        temp_size = 0
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

    @ai_input_src.setter
    def ai_input_src(self, val):
        cfunc = lib_importer.windll.ArtDAQ_SetAIInputSrc
        if cfunc.argtypes is None:
            with cfunc.arglock:
                if cfunc.argtypes is None:
                    cfunc.argtypes = [
                        lib_importer.task_handle, ctypes_byte_str,
                        ctypes_byte_str]

        error_code = cfunc(
            self._handle, self._name, val)
        check_for_error(error_code)


    @property
    def ai_max(self):
        """
        str: Specifies the maximum value you expect to measure.
        This value is in the units you specify with a units property.
        When you query this property, it returns the coerced maximum value that
        the device can measure with the current settings.
        """
        val = ctypes.c_double()
        cfunc = lib_importer.windll.ArtDAQ_GetAIMax
        if cfunc.argtypes is None:
            with cfunc.arglock:
                if cfunc.argtypes is None:
                    cfunc.argtypes = [
                        lib_importer.task_handle, ctypes_byte_str,
                        ctypes.POINTER(ctypes.c_double)]

        error_code = cfunc(self._handle, self._name, ctypes.byref(val))
        check_for_error(error_code)
        return val.value

    @ai_max.setter
    def ai_max(self, val):
        cfunc = lib_importer.windll.ArtDAQ_SetAIMax
        if cfunc.argtypes is None:
            with cfunc.arglock:
                if cfunc.argtypes is None:
                    cfunc.argtypes = [
                        lib_importer.task_handle, ctypes_byte_str, ctypes.c_double]

        error_code = cfunc(
            self._handle, self._name, val)
        check_for_error(error_code)

    @ai_max.deleter
    def ai_max(self):
        cfunc = lib_importer.windll.ArtDAQ_ResetAIMax
        if cfunc.argtypes is None:
            with cfunc.arglock:
                if cfunc.argtypes is None:
                    cfunc.argtypes = [
                        lib_importer.task_handle, ctypes_byte_str]

        error_code = cfunc(self._handle)
        check_for_error(error_code)


    @property
    def ai_min(self):
        """
        Specifies the minimum value you expect to measure.
        This value is in the units you specify with a units property.
        When you query this property, it returns the coerced minimum
        value that the device can measure with the current settings.
        """
        val = ctypes.c_double()
        cfunc = lib_importer.windll.ArtDAQ_GetAIMin
        if cfunc.argtypes is None:
            with cfunc.arglock:
                if cfunc.argtypes is None:
                    cfunc.argtypes = [
                        lib_importer.task_handle, ctypes_byte_str, ctypes.POINTER(ctypes.c_double)]

        error_code = cfunc(self._handle, self._name, ctypes.byref(val))
        check_for_error(error_code)
        return val.value

    @ai_min.setter
    def ai_min(self, val):
        cfunc = lib_importer.windll.ArtDAQ_SetAIMin
        if cfunc.argtypes is None:
            with cfunc.arglock:
                if cfunc.argtypes is None:
                    cfunc.argtypes = [
                        lib_importer.task_handle, ctypes_byte_str, ctypes.c_double]

        error_code = cfunc(
            self._handle, self._name, val)
        check_for_error(error_code)

    @ai_min.deleter
    def ai_min(self):
        cfunc = lib_importer.windll.ArtDAQ_ResetAIMin
        if cfunc.argtypes is None:
            with cfunc.arglock:
                if cfunc.argtypes is None:
                    cfunc.argtypes = [
                        lib_importer.task_handle, ctypes_byte_str]

        error_code = cfunc(self._handle)
        check_for_error(error_code)

    @property
    def ai_customscalename(self):
        """
        Specifies the name of a custom scale for the channel.
        """
        cfunc = lib_importer.windll.ArtDAQ_GetAICustomScaleName
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

    @ai_customscalename.setter
    def ai_customscalename(self, val):
        cfunc = lib_importer.windll.ArtDAQ_SetAICustomScaleName
        if cfunc.argtypes is None:
            with cfunc.arglock:
                if cfunc.argtypes is None:
                    cfunc.argtypes = [
                        lib_importer.task_handle, ctypes_byte_str, ctypes_byte_str]

        error_code = cfunc(
            self._handle, self._name, val)
        check_for_error(error_code)

    @ai_customscalename.deleter
    def ai_customscalename(self):
        cfunc = lib_importer.windll.ArtDAQ_ResetAICustomScaleName
        if cfunc.argtypes is None:
            with cfunc.arglock:
                if cfunc.argtypes is None:
                    cfunc.argtypes = [
                        lib_importer.task_handle, ctypes_byte_str]

        error_code = cfunc(self._handle)
        check_for_error(error_code)

    @property
    def ai_meastype(self):
        """
        Indicates the measurement to take with the analog input channel and in some cases,
        such as for temperature measurements, the sensor to use.
        """
        val = ctypes.c_int32()
        cfunc = lib_importer.windll.ArtDAQ_GetAIMeasType
        if cfunc.argtypes is None:
            with cfunc.arglock:
                if cfunc.argtypes is None:
                    cfunc.argtypes = [
                        lib_importer.task_handle, ctypes_byte_str, ctypes.POINTER(ctypes.c_int32)]

        error_code = cfunc(self._handle, self._name, ctypes.byref(val))
        check_for_error(error_code)
        return AIMeasurementType(val.value)

    @property
    def ai_termcfg(self):
        """
        Specifies the terminal configuration for the channel.
        """
        val = ctypes.c_int32
        cfunc = lib_importer.windll.ArtDAQ_GetAITermCfg
        if cfunc.argtypes is None:
            with cfunc.arglock:
                if cfunc.argtypes is None:
                    cfunc.argtypes = [
                        lib_importer.task_handle, ctypes_byte_str, ctypes.POINTER(ctypes.c_int32)]

        error_code = cfunc(self._handle, self._name, ctypes.byref(val))
        check_for_error(error_code)
        return InputTermCfg(val.value)

    @ai_termcfg.setter
    def ai_termcfg(self, val):
        cfunc = lib_importer.windll.ArtDAQ_SetAITermCfg
        if cfunc.argtypes is None:
            with cfunc.arglock:
                if cfunc.argtypes is None:
                    cfunc.argtypes = [
                        lib_importer.task_handle, ctypes_byte_str, ctypes.c_int32]

        error_code = cfunc(
            self._handle, self._name, val)
        check_for_error(error_code)

    @ai_termcfg.deleter
    def ai_termcfg(self):
        cfunc = lib_importer.windll.ArtDAQ_ResetAITermCfg
        if cfunc.argtypes is None:
            with cfunc.arglock:
                if cfunc.argtypes is None:
                    cfunc.argtypes = [
                        lib_importer.task_handle, ctypes_byte_str]

        error_code = cfunc(self._handle)
        check_for_error(error_code)

    @property
    def ai_auto_zero_mode(self):
        """
        Specifies how often to measure ground.
        ArtDAQ subtracts the measured ground voltage from every sample.
        """
        val = ctypes.c_int32()
        cfunc = lib_importer.windll.ArtDAQ_GetAIAutoZeroMode
        if cfunc.argtypes is None:
            with cfunc.arglock:
                if cfunc.argtypes is None:
                    cfunc.argtypes = [
                        lib_importer.task_handle, ctypes_byte_str, ctypes.POINTER(ctypes.c_int32)]

        error_code = cfunc(self._handle, self._name, ctypes.byref(val))
        check_for_error(error_code)
        return AutoZeroType(val.value)

    @ai_auto_zero_mode.setter
    def ai_auto_zero_mode(self, val):
        cfunc = lib_importer.windll.ArtDAQ_SetAIAutoZeroMode
        if cfunc.argtypes is None:
            with cfunc.arglock:
                if cfunc.argtypes is None:
                    cfunc.argtypes = [
                        lib_importer.task_handle, ctypes_byte_str, ctypes.c_int32]

        error_code = cfunc(
            self._handle, self._name, val)
        check_for_error(error_code)

    @ai_auto_zero_mode.deleter
    def ai_auto_zero_mode(self):
        cfunc = lib_importer.windll.ArtDAQ_ResetAIAutoZeroMode
        if cfunc.argtypes is None:
            with cfunc.arglock:
                if cfunc.argtypes is None:
                    cfunc.argtypes = [
                        lib_importer.task_handle, ctypes_byte_str]

        error_code = cfunc(self)
        check_for_error(error_code)

    @property
    def ai_open_thrmcpl_detect_enable(self):
        """
        Specifies whether to apply the open thermocouple detection bias voltage
        to the channel. Changing the value of this property on a channel may require
        settling time before the data returned is valid. To compensate for this
        settling time, discard unsettled data or add a delay between committing
        and starting the task. Refer to your device specifications for the required
        settling time. When open thermocouple detection ...
        """
        val = ctypes.c_bool()
        cfunc = lib_importer.windll.ArtDAQ_GetAIOpenThrmcplDetectEnable
        if cfunc.argtypes is None:
            with cfunc.arglock:
                if cfunc.argtypes is None:
                    cfunc.argtypes = [
                        lib_importer.task_handle, ctypes_byte_str, ctypes.POINTER(ctypes.c_bool)]

        error_code = cfunc(self._handle, self._name, ctypes.byref(val))
        check_for_error(error_code)
        return val.value

    @ai_open_thrmcpl_detect_enable.setter
    def ai_open_thrmcpl_detect_enable(self, val):
        cfunc = lib_importer.windll.ArtDAQ_SetAIOpenThrmcplDetectEnable
        if cfunc.argtypes is None:
            with cfunc.arglock:
                if cfunc.argtypes is None:
                    cfunc.argtypes = [
                        lib_importer.task_handle, ctypes_byte_str, ctypes.c_uint32]

        error_code = cfunc(
            self._handle, self._name, val)
        check_for_error(error_code)

    @ai_open_thrmcpl_detect_enable.deleter
    def ai_open_thrmcpl_detect_enable(self):
        cfunc = lib_importer.windll.ArtDAQ_ResetAIOpenThrmcplDetectEnable
        if cfunc.argtypes is None:
            with cfunc.arglock:
                if cfunc.argtypes is None:
                    cfunc.argtypes = [
                        lib_importer.task_handle, ctypes_byte_str]

        error_code = cfunc(self._handle, self._name)
        check_for_error(error_code)

    @property
    def ai_rtd_type(self):
        """
        Specifies the type of RTD connected to the channel.
        """
        val = ctypes.c_int32()
        cfunc = lib_importer.windll.ArtDAQ_GetAIRTDType
        if cfunc.argtypes is None:
            with cfunc.arglock:
                if cfunc.argtypes is None:
                    cfunc.argtypes = [
                        lib_importer.task_handle, ctypes_byte_str, ctypes.POINTER(ctypes.c_int32)]

        error_code = cfunc(self._handle, self._name, ctypes.byref(val))
        check_for_error(error_code)
        return val.value

    @ai_rtd_type.setter
    def ai_rtd_type(self, val):
        cfunc = lib_importer.windll.ArtDAQ_SetAIRTDType
        if cfunc.argtypes is None:
            with cfunc.arglock:
                if cfunc.argtypes is None:
                    cfunc.argtypes = [
                        lib_importer.task_handle, ctypes_byte_str, ctypes.c_int32]

        error_code = cfunc(
            self._handle, self._name, val)
        check_for_error(error_code)

    @ai_rtd_type.deleter
    def ai_rtd_type(self):
        cfunc = lib_importer.windll.ArtDAQ_ResetAIRTDType
        if cfunc.argtypes is None:
            with cfunc.arglock:
                if cfunc.argtypes is None:
                    cfunc.argtypes = [
                        lib_importer.task_handle, ctypes_byte_str]

        error_code = cfunc(self._handle, self._name)
        check_for_error(error_code)

    @property
    def ai_rtd_r0(self):
        """
        Specifies in ohms the sensor resistance at 0 deg C.
        The Callendar-Van Dusen equation requires this value.
        Refer to the sensor documentation to determine this value.
        """
        val = ctypes.c_double
        cfunc = lib_importer.windll.ArtDAQ_GetAIRTDR0
        if cfunc.argtypes is None:
            with cfunc.arglock:
                if cfunc.argtypes is None:
                    cfunc.argtypes = [
                        lib_importer.task_handle, ctypes_byte_str, ctypes.POINTER(ctypes.c_double)]

        error_code = cfunc(self._handle, self._name, ctypes.byref(val))
        check_for_error(error_code)
        return val.value

    @ai_rtd_r0.setter
    def ai_rtd_r0(self, val):
        cfunc = lib_importer.windll.ArtDAQ_SetAIRTDR0
        if cfunc.argtypes is None:
            with cfunc.arglock:
                if cfunc.argtypes is None:
                    cfunc.argtypes = [
                        lib_importer.task_handle, ctypes_byte_str, ctypes.c_double]

        error_code = cfunc(
            self._handle, self._name, val)
        check_for_error(error_code)

    @ai_rtd_r0.deleter
    def ai_rtd_r0(self):
        cfunc = lib_importer.windll.ArtDAQ_ResetAIRTDR0
        if cfunc.argtypes is None:
            with cfunc.arglock:
                if cfunc.argtypes is None:
                    cfunc.argtypes = [
                        lib_importer.task_handle, ctypes_byte_str]

        error_code = cfunc(self._handle, self._name)
        check_for_error(error_code)

    @property
    def ai_rtd_A(self):
        """
        Specifies the 'A' constant of the Callendar-Van Dusen equation.
        ArtDAQ requires this value when you use a custom RTD.
        """
        val = ctypes.c_double()
        cfunc = lib_importer.windll.ArtDAQ_GetAIRTDA
        if cfunc.argtypes is None:
            with cfunc.arglock:
                if cfunc.argtypes is None:
                    cfunc.argtypes = [
                        lib_importer.task_handle, ctypes_byte_str, ctypes.POINTER(ctypes.c_double)]

        error_code = cfunc(self._handle, self._name)
        check_for_error(error_code)

    @ai_rtd_A.setter
    def ai_rtd_A(self, val):
        cfunc = lib_importer.windll.ArtDAQ_SetAIRTDA
        if cfunc.argtypes is None:
            with cfunc.arglock:
                if cfunc.argtypes is None:
                    cfunc.argtypes = [
                        lib_importer.task_handle, ctypes_byte_str, ctypes.c_double]

        error_code = cfunc(
            self._handle, self._name, val)
        check_for_error(error_code)

    @ai_rtd_A.deleter
    def ai_rtd_A(self):
        cfunc = lib_importer.windll.ArtDAQ_ResetAIRTDA
        if cfunc.argtypes is None:
            with cfunc.arglock:
                if cfunc.argtypes is None:
                    cfunc.argtypes = [
                        lib_importer.task_handle, ctypes_byte_str]

        error_code = cfunc(self._handle, self._name)
        check_for_error(error_code)

    @property
    def ai_rtd_B(self):
        """
        Specifies the 'B' constant of the Callendar-Van Dusen equation.
        ArtDAQ requires this value when you use a custom RTD.
        """
        val = ctypes.c_double()
        cfunc = lib_importer.windll.ArtDAQ_GetAIRTDB
        if cfunc.argtypes is None:
            with cfunc.arglock:
                if cfunc.argtypes is None:
                    cfunc.argtypes = [
                        lib_importer.task_handle, ctypes_byte_str, ctypes.POINTER(ctypes.c_double)]

        error_code = cfunc(self._handle, self._name, ctypes.byref(val))
        check_for_error(error_code)

    @ai_rtd_B.setter
    def ai_rtd_B(self, val):
        cfunc = lib_importer.windll.ArtDAQ_SetAIRTDB
        if cfunc.argtypes is None:
            with cfunc.arglock:
                if cfunc.argtypes is None:
                    cfunc.argtypes = [
                        lib_importer.task_handle, ctypes_byte_str, ctypes.c_double]

        error_code = cfunc(
            self._handle, self._name, val)
        check_for_error(error_code)

    @ai_rtd_B.deleter
    def ai_rtd_B(self):
        cfunc = lib_importer.windll.ArtDAQ_ResetAIRTDB
        if cfunc.argtypes is None:
            with cfunc.arglock:
                if cfunc.argtypes is None:
                    cfunc.argtypes = [
                        lib_importer.task_handle, ctypes_byte_str]

        error_code = cfunc(self._handle, self._name)
        check_for_error(error_code)

    @property
    def ai_rtd_C(self):
        """
        Specifies the 'C' constant of the Callendar-Van Dusen equation.
        ArtDAQ requires this value when you use a custom RTD.
        """
        val = ctypes.c_double()
        cfunc = lib_importer.windll.ArtDAQ_GetAIRTDC
        if cfunc.argtypes is None:
            with cfunc.arglock:
                if cfunc.argtypes is None:
                    cfunc.argtypes = [
                        lib_importer.task_handle, ctypes_byte_str, ctypes.POINTER(ctypes.c_double)]

        error_code = cfunc(self._handle, self._name, ctypes.byref(val))
        check_for_error(error_code)
        return val.value

    @ai_rtd_C.setter
    def ai_rtd_C(self, val):
        cfunc = lib_importer.windll.ArtDAQ_SetAIRTDC
        if cfunc.argtypes is None:
            with cfunc.arglock:
                if cfunc.argtypes is None:
                    cfunc.argtypes = [
                        lib_importer.task_handle, ctypes_byte_str, ctypes.c_double]

        error_code = cfunc(
            self._handle, self._name, val)
        check_for_error(error_code)

    @ai_rtd_C.deleter
    def ai_rtd_C(self):
        cfunc = lib_importer.windll.ArtDAQ_ResetAIRTDC
        if cfunc.argtypes is None:
            with cfunc.arglock:
                if cfunc.argtypes is None:
                    cfunc.argtypes = [
                        lib_importer.task_handle, ctypes_byte_str]

        error_code = cfunc(self._handle, self._name)
        check_for_error(error_code)

    @property
    def ai_thrmstr_A(self):
        """
        Specifies the 'A' constant of the Steinhart-Hart thermistor equation.
        """
        val = ctypes.c_double()
        cfunc = lib_importer.windll.ArtDAQ_GetAIThrmstrA
        if cfunc.argtypes is None:
            with cfunc.arglock:
                if cfunc.argtypes is None:
                    cfunc.argtypes = [
                        lib_importer.task_handle, ctypes_byte_str, ctypes.POINTER(ctypes.c_double)]

        error_code = cfunc(self._handle, self._name, ctypes.byref(val))
        check_for_error(error_code)
        return val.value

    @ai_thrmstr_A.setter
    def ai_thrmstr_A(self, val):
        cfunc = lib_importer.windll.ArtDAQ_SetAIThrmstrA
        if cfunc.argtypes is None:
            with cfunc.arglock:
                if cfunc.argtypes is None:
                    cfunc.argtypes = [
                        lib_importer.task_handle, ctypes_byte_str, ctypes.c_double]

        error_code = cfunc(
            self._handle, self._name, val)
        check_for_error(error_code)

    @ai_thrmstr_A.deleter
    def ai_thrmstr_A(self):
        cfunc = lib_importer.windll.ArtDAQ_ResetAIThrmstrA
        if cfunc.argtypes is None:
            with cfunc.arglock:
                if cfunc.argtypes is None:
                    cfunc.argtypes = [
                        lib_importer.task_handle, ctypes_byte_str]

        error_code = cfunc(self._handle, self._name)
        check_for_error(error_code)

    @property
    def ai_thrmstr_B(self):
        """
        Specifies the 'B' constant of the Steinhart-Hart thermistor equation.
        """
        val = ctypes.c_double()
        cfunc = lib_importer.windll.ArtDAQ_GetAIThrmstrB
        if cfunc.argtypes is None:
            with cfunc.arglock:
                if cfunc.argtypes is None:
                    cfunc.argtypes = [
                        lib_importer.task_handle, ctypes_byte_str, ctypes.POINTER(ctypes.c_double)]

        error_code = cfunc(self._handle, self._name, ctypes.byref(val))
        check_for_error(error_code)
        return val.value

    @ai_thrmstr_B.setter
    def ai_thrmstr_B(self, val):
        cfunc = lib_importer.windll.ArtDAQ_SetAIThrmstrB
        if cfunc.argtypes is None:
            with cfunc.arglock:
                if cfunc.argtypes is None:
                    cfunc.argtypes = [
                        lib_importer.task_handle, ctypes_byte_str, ctypes.c_double]

        error_code = cfunc(
            self._handle, self._name, val)
        check_for_error(error_code)

    @ai_thrmstr_B.deleter
    def ai_thrmstr_B(self):
        cfunc = lib_importer.windll.ArtDAQ_ResetAIThrmstrB
        if cfunc.argtypes is None:
            with cfunc.arglock:
                if cfunc.argtypes is None:
                    cfunc.argtypes = [
                        lib_importer.task_handle, ctypes_byte_str]

        error_code = cfunc(self._handle, self._name)
        check_for_error(error_code)

    @property
    def ai_thrmstr_C(self):
        """
       Specifies the 'C' constant of the Steinhart-Hart thermistor equation.
        """
        val = ctypes.c_double()
        cfunc = lib_importer.windll.ArtDAQ_GetAIThrmstrC
        if cfunc.argtypes is None:
            with cfunc.arglock:
                if cfunc.argtypes is None:
                    cfunc.argtypes = [
                        lib_importer.task_handle, ctypes_byte_str, ctypes.POINTER(ctypes.c_double)]

        error_code = cfunc(self._handle, self._name, ctypes.byref(val))
        check_for_error(error_code)
        return val.value

    @ai_thrmstr_C.setter
    def ai_thrmstr_C(self, val):
        cfunc = lib_importer.windll.ArtDAQ_SetAIThrmstrC
        if cfunc.argtypes is None:
            with cfunc.arglock:
                if cfunc.argtypes is None:
                    cfunc.argtypes = [
                        lib_importer.task_handle, ctypes_byte_str, ctypes.c_double]

        error_code = cfunc(
            self._handle, self._name, val)
        check_for_error(error_code)

    @ai_thrmstr_C.deleter
    def ai_thrmstr_C(self):
        cfunc = lib_importer.windll.ArtDAQ_ResetAIThrmstrC
        if cfunc.argtypes is None:
            with cfunc.arglock:
                if cfunc.argtypes is None:
                    cfunc.argtypes = [
                        lib_importer.task_handle, ctypes_byte_str]

        error_code = cfunc(self._handle, self._name)
        check_for_error(error_code)

    @property
    def ai_thrmstr_R1(self):
        """
        Specifies in ohms the value of the reference resistor for the thermistor
        if you use voltage excitation. ArtDAQ ignores this value for current excitation.
        """
        val = ctypes.c_double()
        cfunc = lib_importer.windll.ArtDAQ_GetAIThrmstrR1
        if cfunc.argtypes is None:
            with cfunc.arglock:
                if cfunc.argtypes is None:
                    cfunc.argtypes = [
                        lib_importer.task_handle, ctypes_byte_str, ctypes.c_double_p]

        error_code = cfunc(self)
        check_for_error(error_code)

    @ai_thrmstr_R1.setter
    def ai_thrmstr_R1(self, val):
        cfunc = lib_importer.windll.ArtDAQ_SetAIThrmstrR1
        if cfunc.argtypes is None:
            with cfunc.arglock:
                if cfunc.argtypes is None:
                    cfunc.argtypes = [
                        lib_importer.task_handle, ctypes_byte_str, ctypes.c_double]

        error_code = cfunc(
            self._handle, self._name, val)
        check_for_error(error_code)

    @ai_thrmstr_R1.deleter
    def ai_thrmstr_R1(self):
        cfunc = lib_importer.windll.ArtDAQ_ResetAIThrmstrR1
        if cfunc.argtypes is None:
            with cfunc.arglock:
                if cfunc.argtypes is None:
                    cfunc.argtypes = [
                        lib_importer.task_handle, ctypes_byte_str]

        error_code = cfunc(self._handle, self._name)
        check_for_error(error_code)

    @property
    def ai_bridge_shuntcal_enable(self):
        """
        Specifies whether to enable a shunt calibration switch.
        Use Shunt Cal Select to select the switch(es) to enable.
        """
        val = ctypes.c_bool()
        cfunc = lib_importer.windll.ArtDAQ_GetAIBridgeShuntCalEnable
        if cfunc.argtypes is None:
            with cfunc.arglock:
                if cfunc.argtypes is None:
                    cfunc.argtypes = [
                        lib_importer.task_handle, ctypes_byte_str, ctypes.POINTER(ctypes.c_bool)]

        error_code = cfunc(self._handle, self._name, ctypes.byref(val))
        check_for_error(error_code)
        return val.value

    @ai_bridge_shuntcal_enable.setter
    def ai_bridge_shuntcal_enable(self, val):
        cfunc = lib_importer.windll.ArtDAQ_SetAIThrmstrR1
        if cfunc.argtypes is None:
            with cfunc.arglock:
                if cfunc.argtypes is None:
                    cfunc.argtypes = [
                        lib_importer.task_handle, ctypes_byte_str, ctypes.c_double]

        error_code = cfunc(
            self._handle, self._name, val)
        check_for_error(error_code)

    @ai_bridge_shuntcal_enable.deleter
    def ai_bridge_shuntcal_enable(self):
        cfunc = lib_importer.windll.ArtDAQ_ResetAIThrmstrR1
        if cfunc.argtypes is None:
            with cfunc.arglock:
                if cfunc.argtypes is None:
                    cfunc.argtypes = [
                        lib_importer.task_handle, ctypes_byte_str]

        error_code = cfunc(self._handle, self._name)
        check_for_error(error_code)





















