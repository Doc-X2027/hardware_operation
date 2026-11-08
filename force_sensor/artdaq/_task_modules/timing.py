from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import ctypes
from artdaq._lib import lib_importer, ctypes_byte_str
from artdaq.errors import check_for_error
from artdaq.constants import (AcquisitionType, Edge, SampleTimingType, OverflowBehavior, UnderflowBehavior)
from artdaq.errors import (
    check_for_error, is_string_buffer_too_small, DaqError, DaqResourceWarning)
class Timing(object):
    """
    Represents the timing configurations for a DAQ task.
    """
    def __init__(self, task_handle):
        self._handle = task_handle

    @property
    def samp_timing_type(self):
        val = ctypes.c_int()
        cfunc = lib_importer.windll.ArtDAQ_GetSampTimingType
        if cfunc.argtypes is None:
            with cfunc.arglock:
                if cfunc.argtypes is None:
                    cfunc.argtypes = [lib_importer.task_handle,
                                      ctypes.POINTER(ctypes.c_int)]
        error_code = cfunc(self._handle, ctypes.byref(val))
        check_for_error(error_code)
        return SampleTimingType.value

    @property
    def mode(self):
        """
        str: Indicates the name of the task.
        """
        cfunc = lib_importer.windll.ArtDAQ_GetTimingAttribute
        if cfunc.argtypes is None:
            with cfunc.arglock:
                if cfunc.argtypes is None:
                    cfunc.argtypes = [
                        lib_importer.task_handle, ctypes.c_int, ctypes.c_char_p,
                        ctypes.c_int]

        temp_size = 256
        while True:
            val = ctypes.create_string_buffer(temp_size)
            size_or_code = cfunc(
                self._handle, 0x1300, val, temp_size)

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

    @property
    def sample_per_chan(self):
        """
        str: Indicates the name of the task.
        """
        cfunc = lib_importer.windll.ArtDAQ_GetTimingAttribute
        if cfunc.argtypes is None:
            with cfunc.arglock:
                if cfunc.argtypes is None:
                    cfunc.argtypes = [
                        lib_importer.task_handle, ctypes.c_int, ctypes.c_char_p,
                        ctypes.c_int]

        temp_size = 256
        while True:
            val = ctypes.create_string_buffer(temp_size)
            size_or_code = cfunc(
                self._handle, 0x1310, val, temp_size)

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

    @property
    def timing_type(self):
        """
        str: Indicates the name of the task.
        """
        cfunc = lib_importer.windll.ArtDAQ_GetTimingAttribute
        if cfunc.argtypes is None:
            with cfunc.arglock:
                if cfunc.argtypes is None:
                    cfunc.argtypes = [
                        lib_importer.task_handle, ctypes.c_int, ctypes.c_char_p,
                        ctypes.c_int]

        temp_size = 256
        while True:
            val = ctypes.create_string_buffer(temp_size)
            size_or_code = cfunc(
                self._handle, 0x1347, val, temp_size)

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

    @property
    def max_rate(self):
        """
        str: Indicates the name of the task.
        """
        cfunc = lib_importer.windll.ArtDAQ_GetTimingAttribute
        if cfunc.argtypes is None:
            with cfunc.arglock:
                if cfunc.argtypes is None:
                    cfunc.argtypes = [
                        lib_importer.task_handle, ctypes.c_int, ctypes.c_char_p,
                        ctypes.c_int]

        temp_size = 256
        while True:
            val = ctypes.create_string_buffer(temp_size)
            size_or_code = cfunc(
                self._handle, 0x22C8, val, temp_size)

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

    @property
    def rate(self):
        """
        str: Indicates the name of the task.
        """
        cfunc = lib_importer.windll.ArtDAQ_GetTimingAttribute
        if cfunc.argtypes is None:
            with cfunc.arglock:
                if cfunc.argtypes is None:
                    cfunc.argtypes = [
                        lib_importer.task_handle, ctypes.c_int, ctypes.c_char_p,
                        ctypes.c_int]

        temp_size = 256
        while True:
            val = ctypes.create_string_buffer(temp_size)
            size_or_code = cfunc(
                self._handle, 0x1344, val, temp_size)

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

    @samp_timing_type.setter
    def samp_timing_type(self, val):
        cfunc = lib_importer.windll.ArtDAQ_SetSampTimingType
        if cfunc.argtypes is None:
            with cfunc.arglock:
                if cfunc.argtypes is None:
                    cfunc.argtypes = [lib_importer.task_handle,
                                      ctypes.c_int]
        error_code = cfunc(self._handle, ctypes.byref(val))
        check_for_error(error_code)

    @samp_timing_type.deleter
    def samp_timing_type(self):
        cfunc = lib_importer.windll.ArtDAQ_ResetSampTimingType
        if cfunc.argtypes is None:
            with cfunc.arglock:
                if cfunc.argtypes is None:
                    cfunc.argtypes = [lib_importer.task_handle]
        error_code = cfunc(self._handle)
        check_for_error(error_code)

    @property
    def sampclk_over_run_behavior(self):
        val = ctypes.c_int()
        cfunc = lib_importer.windll.ArtDAQ_GetSampClkOverrunBehavior
        if cfunc.argtypes is None:
            with cfunc.arglock:
                if cfunc.argtypes is None:
                    cfunc.argtypes = [lib_importer.task_handle,
                                      ctypes.POINTER(ctypes.c_int)]
        error_code = cfunc(self._handle, ctypes.byref(val))
        check_for_error(error_code)
        return OverflowBehavior.value

    @sampclk_over_run_behavior.setter
    def sampclk_over_run_behavior(self, val):
        cfunc = lib_importer.windll.ArtDAQ_SetSampClkOverrunBehavior
        if cfunc.argtypes is None:
            with cfunc.arglock:
                if cfunc.argtypes is None:
                    cfunc.argtypes = [lib_importer.task_handle,
                                      ctypes.c_int]
        error_code = cfunc(self._handle, ctypes.byref(val))
        check_for_error(error_code)

    @sampclk_over_run_behavior.deleter
    def sampclk_over_run_behavior(self):
        cfunc = lib_importer.windll.ArtDAQ_ResetSampClkOverrunBehavior
        if cfunc.argtypes is None:
            with cfunc.arglock:
                if cfunc.argtypes is None:
                    cfunc.argtypes = [lib_importer.task_handle]
        error_code = cfunc(self._handle)
        check_for_error(error_code)

    @property
    def sampclk_under_flow_behavior(self):
        val = ctypes.c_int()
        cfunc = lib_importer.windll.ArtDAQ_GetSampClkUnderflowBehavior
        if cfunc.argtypes is None:
            with cfunc.arglock:
                if cfunc.argtypes is None:
                    cfunc.argtypes = [lib_importer.task_handle,
                                      ctypes.POINTER(ctypes.c_int)]
        error_code = cfunc(self._handle, ctypes.byref(val))
        check_for_error(error_code)
        return UnderflowBehavior.value

    @sampclk_under_flow_behavior.setter
    def sampclk_under_flow_behavior(self, val):
        cfunc = lib_importer.windll.ArtDAQ_SetSampClkUnderflowBehavior
        if cfunc.argtypes is None:
            with cfunc.arglock:
                if cfunc.argtypes is None:
                    cfunc.argtypes = [lib_importer.task_handle,
                                      ctypes.c_int]
        error_code = cfunc(self._handle, ctypes.byref(val))
        check_for_error(error_code)

    @sampclk_under_flow_behavior.deleter
    def sampclk_under_flow_behavior(self):
        cfunc = lib_importer.windll.ArtDAQ_ResetSampClkUnderflowBehavior
        if cfunc.argtypes is None:
            with cfunc.arglock:
                if cfunc.argtypes is None:
                    cfunc.argtypes = [lib_importer.task_handle]
        error_code = cfunc(self._handle)
        check_for_error(error_code)

    @property
    def implicit_under_flow_behavior(self):
        val = ctypes.c_int()
        cfunc = lib_importer.windll.ArtDAQ_GetImplicitUnderflowBehavior
        if cfunc.argtypes is None:
            with cfunc.arglock:
                if cfunc.argtypes is None:
                    cfunc.argtypes = [lib_importer.task_handle,
                                      ctypes.POINTER(ctypes.c_int)]
        error_code = cfunc(self._handle, ctypes.byref(val))
        check_for_error(error_code)
        return UnderflowBehavior.value

    @sampclk_under_flow_behavior.setter
    def sampclk_under_flow_behavior(self, val):
        cfunc = lib_importer.windll.ArtDAQ_SetImplicitUnderflowBehavior
        if cfunc.argtypes is None:
            with cfunc.arglock:
                if cfunc.argtypes is None:
                    cfunc.argtypes = [lib_importer.task_handle,
                                      ctypes.c_int]
        error_code = cfunc(self._handle, ctypes.byref(val))
        check_for_error(error_code)

    @sampclk_under_flow_behavior.deleter
    def sampclk_under_flow_behavior(self):
        cfunc = lib_importer.windll.ArtDAQ_ResetImplicitUnderflowBehavior
        if cfunc.argtypes is None:
            with cfunc.arglock:
                if cfunc.argtypes is None:
                    cfunc.argtypes = [lib_importer.task_handle]
        error_code = cfunc(self._handle)
        check_for_error(error_code)

    def ai_conv_src(self, val, active_edge=Edge.RISING):
        cfunc = lib_importer.windll.ArtDAQ_SetAIConvClk
        if cfunc.argtypes is None:
            with cfunc.arglock:
                if cfunc.argtypes is None:
                    cfunc.argtypes = [
                        lib_importer.task_handle, ctypes_byte_str, ctypes.c_int]

        error_code = cfunc(
            self._handle, val, active_edge.value)
        check_for_error(error_code)

    def samp_clk_timebase_src(self, val):
        cfunc = lib_importer.windll.ArtDAQ_SetSampClkTimebaseSrc
        if cfunc.argtypes is None:
            with cfunc.arglock:
                if cfunc.argtypes is None:
                    cfunc.argtypes = [
                        lib_importer.task_handle, ctypes_byte_str]

        error_code = cfunc(
            self._handle, val)
        check_for_error(error_code)

    def samp_clk_timebase_outputterm(self, val):
        cfunc = lib_importer.windll.ArtDAQ_SetExportedSampClkTimebaseOutputTerm
        if cfunc.argtypes is None:
            with cfunc.arglock:
                if cfunc.argtypes is None:
                    cfunc.argtypes = [
                        lib_importer.task_handle, ctypes_byte_str]
        error_code = cfunc(
             self._handle, val)
        check_for_error(error_code)

    def ref_clk_src(self, val):
        cfunc = lib_importer.windll.ArtDAQ_SetRefClkSrc
        if cfunc.argtypes is None:
            with cfunc.arglock:
                if cfunc.argtypes is None:
                    cfunc.argtypes = [
                        lib_importer.task_handle, ctypes_byte_str]

        error_code = cfunc(
            self._handle, val)
        check_for_error(error_code)

    def sync_pulse_src(self, val):
        cfunc = lib_importer.windll.ArtDAQ_SetSyncPulseSrc
        if cfunc.argtypes is None:
            with cfunc.arglock:
                if cfunc.argtypes is None:
                    cfunc.argtypes = [
                        lib_importer.task_handle, ctypes_byte_str]

        error_code = cfunc(
            self._handle, val)
        check_for_error(error_code)

    def samp_sync_pulse_Event_outputterm(self, val):
        cfunc = lib_importer.windll.ArtDAQ_SetExportedSyncPulseEventOutputTerm
        if cfunc.argtypes is None:
            with cfunc.arglock:
                if cfunc.argtypes is None:
                    cfunc.argtypes = [
                        lib_importer.task_handle, ctypes_byte_str]
        error_code = cfunc(
            self._handle, val)
        check_for_error(error_code)

    def cfg_implicit_timing(
            self, sample_mode=AcquisitionType.FINITE, samps_per_chan=100):
        """
        Sets only the number of samples to acquire or generate without
        specifying timing. Typically, you should use this instance when
        the task does not require sample timing, such as tasks that use
        counters for buffered frequency measurement, buffered period
        measurement, or pulse train generation. For finite counter
        output tasks, **samps_per_chan** is the number of pulses to
        generate.

        Args:
            sample_mode (Optional[artdaq.constants.AcquisitionType]): 
                Specifies if the task acquires or generates samples
                continuously or if it acquires or generates a finite
                number of samples.
            samps_per_chan (Optional[long]): Specifies the number of
                samples to acquire or generate for each channel in the
                task if **sample_mode** is **FINITE_SAMPLES**. If
                **sample_mode** is **CONTINUOUS_SAMPLES**, DAQ uses
                this value to determine the buffer size. This function
                returns an error if the specified value is negative.
        """
        cfunc = lib_importer.windll.ArtDAQ_CfgImplicitTiming
        if cfunc.argtypes is None:
            with cfunc.arglock:
                if cfunc.argtypes is None:
                    cfunc.argtypes = [
                        lib_importer.task_handle, ctypes.c_int,
                        ctypes.c_ulonglong]

        error_code = cfunc(
            self._handle, sample_mode.value, samps_per_chan)
        check_for_error(error_code)

    def cfg_samp_clk_timing(
            self, source="", rate=1000, active_edge=Edge.RISING,
            sample_mode=AcquisitionType.FINITE, samps_per_chan=1000):
        """
        Sets the source of the Sample Clock, the rate of the Sample
        Clock, and the number of samples to acquire or generate.

        Args:
            rate (float): Specifies the sampling rate in samples per
                channel per second. If you use an external source for
                the Sample Clock, set this input to the maximum expected
                rate of that clock.
            source (Optional[str]): Specifies the source terminal of the
                Sample Clock. Leave this input unspecified to use the
                default onboard clock of the device.
            active_edge (Optional[artdaq.constants.Edge]): Specifies on
                which edges of Sample Clock pulses to acquire or
                generate samples.
            sample_mode (Optional[artdaq.constants.AcquisitionType]): 
                Specifies if the task acquires or generates samples
                continuously or if it acquires or generates a finite
                number of samples.
            samps_per_chan (Optional[long]): Specifies the number of
                samples to acquire or generate for each channel in the
                task if **sample_mode** is **FINITE_SAMPLES**. If
                **sample_mode** is **CONTINUOUS_SAMPLES**, DAQ uses
                this value to determine the buffer size. This function
                returns an error if the specified value is negative.
        """
        cfunc = lib_importer.windll.ArtDAQ_CfgSampClkTiming
        if cfunc.argtypes is None:
            with cfunc.arglock:
                if cfunc.argtypes is None:
                    cfunc.argtypes = [
                        lib_importer.task_handle, ctypes_byte_str,
                        ctypes.c_double, ctypes.c_int, ctypes.c_int,
                        ctypes.c_int]

        error_code = cfunc(
            self._handle, source, rate, active_edge.value, sample_mode.value,samps_per_chan)
        check_for_error(error_code)