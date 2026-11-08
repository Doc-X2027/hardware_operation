from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import ctypes

from artdaq._lib import (
    lib_importer, ctypes_byte_str)
from artdaq.errors import (check_for_error, is_string_buffer_too_small)
from artdaq._task_modules.channels.channel import Channel
from artdaq.constants import (Edge, ToggleIdleState)


class CIOChannel(Channel):
    """
    Represents one or more counter input virtual channels and their properties.
    """
    __slots__ = []

    def __repr__(self):
        return 'CIOChannel(name={0})'.format(self._name)

    @property
    def ci_meas_type(self):
        """
        :class:`artdaq.constants.UsageTypeCI`: Indicates the
            measurement to take with the channel.
        """
        return 0

    def cfg_ci_count_edges_count_reset(
            self, source="", reset_count=0, active_edge=Edge.RISING, dig_fltr_min_pulse_width=0.0):

        """
        reset edge count at the ci countEdges mode
        """
        cfunc = lib_importer.windll.ArtDAQ_CfgCICountEdgesCountReset
        if cfunc.argtypes is None:
            with cfunc.arglock:
                if cfunc.argtypes is None:
                    cfunc.argtypes = [
                        lib_importer.task_handle, ctypes_byte_str, ctypes.c_uint,
                        ctypes.c_int, ctypes.c_double]

        error_code = cfunc(
            self._handle, source, reset_count, active_edge.value, dig_fltr_min_pulse_width)
        check_for_error(error_code)

    def ci_count_edges_count_reset_disable(self):
        cfunc = lib_importer.windll.ArtDAQ_DisableCICountEdgesCountReset
        if cfunc.argtypes is None:
            with cfunc.arglock:
                if cfunc.argtypes is None:
                    cfunc.argtypes = [
                        lib_importer.task_handle]

        error_code = cfunc(self._handle)
        check_for_error(error_code)

    @property
    def ci_source_dig_fltr_min_pulse_width(self):
        """
        Specifies in seconds the minimum pulse width the filter recognizes.
        """
        val = ctypes.c_double()
        cfunc = lib_importer.windll.ArtDAQ_GetCISourceDigFltrMinPulseWidth
        if cfunc.argtypes is None:
            with cfunc.arglock:
                if cfunc.argtypes is None:
                    cfunc.argtypes = [
                        lib_importer.task_handle, ctypes_byte_str, ctypes.POINTER(ctypes.c_double)]

        error_code = cfunc(self._handle, self._name, ctypes.byref(val))
        check_for_error(error_code)
        val.value

    @ci_source_dig_fltr_min_pulse_width.setter
    def ci_source_dig_fltr_min_pulse_width(self, val):
        cfunc = lib_importer.windll.ArtDAQ_SetCISourceDigFltrMinPulseWidth
        if cfunc.argtypes is None:
            with cfunc.arglock:
                if cfunc.argtypes is None:
                    cfunc.argtypes = [
                        lib_importer.task_handle, ctypes_byte_str, ctypes.c_double]

        error_code = cfunc(
            self._handle, self._name, val)
        check_for_error(error_code)

    @ci_source_dig_fltr_min_pulse_width.deleter
    def ci_source_dig_fltr_min_pulse_width(self):
        cfunc = lib_importer.windll.ArtDAQ_ResetCISourceDigFltrMinPulseWidth
        if cfunc.argtypes is None:
            with cfunc.arglock:
                if cfunc.argtypes is None:
                    cfunc.argtypes = [
                        lib_importer.task_handle, ctypes_byte_str]

        error_code = cfunc(self)
        check_for_error(error_code)

    @property
    def ci_gate_dig_fltr_min_pulse_width(self):
        """
        Specifies in seconds the minimum pulse width the filter recognizes.
        """
        val = ctypes.c_double()
        cfunc = lib_importer.windll.ArtDAQ_GetCIGateDigFltrMinPulseWidth
        if cfunc.argtypes is None:
            with cfunc.arglock:
                if cfunc.argtypes is None:
                    cfunc.argtypes = [
                        lib_importer.task_handle, ctypes_byte_str, ctypes.POINTER(ctypes.c_double)]

        error_code = cfunc(self._handle, self._name, ctypes.byref(val))
        check_for_error(error_code)
        return val.value

    @ci_gate_dig_fltr_min_pulse_width.setter
    def ci_gate_dig_fltr_min_pulse_width(self, val):
        cfunc = lib_importer.windll.ArtDAQ_SetCIGateDigFltrMinPulseWidth
        if cfunc.argtypes is None:
            with cfunc.arglock:
                if cfunc.argtypes is None:
                    cfunc.argtypes = [
                        lib_importer.task_handle, ctypes_byte_str, ctypes.c_double]

        error_code = cfunc(
            self._handle, self._name, val)
        check_for_error(error_code)

    @ci_gate_dig_fltr_min_pulse_width.deleter
    def ci_gate_dig_fltr_min_pulse_width(self):
        cfunc = lib_importer.windll.ArtDAQ_ResetCIGateDigFltrMinPulseWidth
        if cfunc.argtypes is None:
            with cfunc.arglock:
                if cfunc.argtypes is None:
                    cfunc.argtypes = [
                        lib_importer.task_handle, ctypes_byte_str]

        error_code = cfunc(self._handle, self._name)
        check_for_error(error_code)

    @property
    def ci_aux_dig_fltr_min_pulse_width(self):
        """
        Specifies in seconds the minimum pulse width the filter recognizes.
        """
        val = ctypes.c_double()
        cfunc = lib_importer.windll.ArtDAQ_GetCIAuxDigFltrMinPulseWidth
        if cfunc.argtypes is None:
            with cfunc.arglock:
                if cfunc.argtypes is None:
                    cfunc.argtypes = [
                        lib_importer.task_handle, ctypes_byte_str, ctypes.POINTER(ctypes.c_double)]

        error_code = cfunc(self._handle, self._name, ctypes.byref(val))
        check_for_error(error_code)
        return val.value

    @ci_aux_dig_fltr_min_pulse_width.setter
    def ci_aux_dig_fltr_min_pulse_width(self, val):
        cfunc = lib_importer.windll.ArtDAQ_SetCIAuxDigFltrMinPulseWidth
        if cfunc.argtypes is None:
            with cfunc.arglock:
                if cfunc.argtypes is None:
                    cfunc.argtypes = [
                        lib_importer.task_handle, ctypes_byte_str, ctypes.c_double]

        error_code = cfunc(
            self._handle, self._name, val)
        check_for_error(error_code)

    @ci_aux_dig_fltr_min_pulse_width.deleter
    def ci_aux_dig_fltr_min_pulse_width(self):
        cfunc = lib_importer.windll.ArtDAQ_ResetCIAuxDigFltrMinPulseWidth
        if cfunc.argtypes is None:
            with cfunc.arglock:
                if cfunc.argtypes is None:
                    cfunc.argtypes = [
                        lib_importer.task_handle, ctypes_byte_str]

        error_code = cfunc(self._handle, self._name)
        check_for_error(error_code)

    @property
    def ci_encoder_A_input_invert(self):
        """
        Specifies whether the A input signal needs to be inverted.
        """
        val = ctypes.c_bool()
        cfunc = lib_importer.windll.ArtDAQ_GetCIEncoderAInputInvert
        if cfunc.argtypes is None:
            with cfunc.arglock:
                if cfunc.argtypes is None:
                    cfunc.argtypes = [
                        lib_importer.task_handle, ctypes_byte_str, ctypes.POINTER(ctypes.c_bool)]

        error_code = cfunc(self._handle, self._name, ctypes.byref(val))
        check_for_error(error_code)
        return val.value

    @ci_encoder_A_input_invert.setter
    def ci_encoder_A_input_invert(self, val):
        cfunc = lib_importer.windll.ArtDAQ_SetCIEncoderAInputInvert
        if cfunc.argtypes is None:
            with cfunc.arglock:
                if cfunc.argtypes is None:
                    cfunc.argtypes = [
                        lib_importer.task_handle, ctypes_byte_str, ctypes.c_uint32]

        error_code = cfunc(
            self._handle, self._name, val)
        check_for_error(error_code)

    @ci_encoder_A_input_invert.deleter
    def ci_encoder_A_input_invert(self):
        cfunc = lib_importer.windll.ArtDAQ_ResetCIEncoderAInputInvert
        if cfunc.argtypes is None:
            with cfunc.arglock:
                if cfunc.argtypes is None:
                    cfunc.argtypes = [
                        lib_importer.task_handle, ctypes_byte_str]

        error_code = cfunc(self._handle, self._name)
        check_for_error(error_code)

    @property
    def ci_encoder_B_input_invert(self):
        """
        Specifies whether the B input signal needs to be inverted.
        """
        val = ctypes.c_bool
        cfunc = lib_importer.windll.ArtDAQ_GetCIEncoderBInputInvert
        if cfunc.argtypes is None:
            with cfunc.arglock:
                if cfunc.argtypes is None:
                    cfunc.argtypes = [
                        lib_importer.task_handle, ctypes_byte_str, ctypes.POINTER(ctypes.c_bool)]

        error_code = cfunc(self._handle, self._name, ctypes.byref(val))
        check_for_error(error_code)
        return val.value

    @ci_encoder_B_input_invert.setter
    def ci_encoder_B_input_invert(self, val):
        cfunc = lib_importer.windll.ArtDAQ_SetCIEncoderBInputInvert
        if cfunc.argtypes is None:
            with cfunc.arglock:
                if cfunc.argtypes is None:
                    cfunc.argtypes = [
                        lib_importer.task_handle, ctypes_byte_str, ctypes.c_uint32]

        error_code = cfunc(
            self._handle, self._name, val)
        check_for_error(error_code)

    @ci_encoder_B_input_invert.deleter
    def ci_encoder_B_input_invert(self):
        cfunc = lib_importer.windll.ArtDAQ_ResetCIEncoderBInputInvert
        if cfunc.argtypes is None:
            with cfunc.arglock:
                if cfunc.argtypes is None:
                    cfunc.argtypes = [
                        lib_importer.task_handle, ctypes_byte_str]

        error_code = cfunc(self._handle, self._name)
        check_for_error(error_code)

    @property
    def ci_encoder_Z_input_invert(self):
        """
        Specifies whether the B input signal needs to be inverted.
        """
        val = ctypes.c_bool()
        cfunc = lib_importer.windll.ArtDAQ_GetCIEncoderZInputInvert
        if cfunc.argtypes is None:
            with cfunc.arglock:
                if cfunc.argtypes is None:
                    cfunc.argtypes = [
                        lib_importer.task_handle, ctypes_byte_str, ctypes.POINTER(ctypes.c_bool)]

        error_code = cfunc(self._handle, self._name, ctypes.byref(val))
        check_for_error(error_code)
        return val.value

    @ci_encoder_Z_input_invert.setter
    def ci_encoder_Z_input_invert(self, val):
        cfunc = lib_importer.windll.ArtDAQ_SetCIEncoderZInputInvert
        if cfunc.argtypes is None:
            with cfunc.arglock:
                if cfunc.argtypes is None:
                    cfunc.argtypes = [
                        lib_importer.task_handle, ctypes_byte_str, ctypes.c_uint32]

        error_code = cfunc(
            self._handle, self._name, val)
        check_for_error(error_code)

    @ci_encoder_Z_input_invert.deleter
    def ci_encoder_Z_input_invert(self):
        cfunc = lib_importer.windll.ArtDAQ_ResetCIEncoderZInputInvert
        if cfunc.argtypes is None:
            with cfunc.arglock:
                if cfunc.argtypes is None:
                    cfunc.argtypes = [
                        lib_importer.task_handle, ctypes_byte_str]

        error_code = cfunc(self._handle, self._name)
        check_for_error(error_code)

    @property
    def co_pulse_term(self):
        """
        Specifies on which terminal to generate pulses.
        """
        cfunc = lib_importer.windll.ArtDAQ_GetCOPulseTerm
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

    @co_pulse_term.setter
    def co_pulse_term(self, val):
        cfunc = lib_importer.windll.ArtDAQ_SetCOPulseTerm
        if cfunc.argtypes is None:
            with cfunc.arglock:
                if cfunc.argtypes is None:
                    cfunc.argtypes = [
                        lib_importer.task_handle, ctypes_byte_str, ctypes_byte_str]

        error_code = cfunc(
            self._handle, self._name, val)
        check_for_error(error_code)

    @co_pulse_term.deleter
    def co_pulse_term(self):
        cfunc = lib_importer.windll.ArtDAQ_ResetCOPulseTerm
        if cfunc.argtypes is None:
            with cfunc.arglock:
                if cfunc.argtypes is None:
                    cfunc.argtypes = [
                        lib_importer.task_handle, ctypes_byte_str]

        error_code = cfunc(self._handle, self._name)
        check_for_error(error_code)

    @property
    def co_count(self):
        """
        Indicates the current value of the count register.
        """
        val = ctypes.c_int32()
        cfunc = lib_importer.windll.ArtDAQ_GetCOCount
        if cfunc.argtypes is None:
            with cfunc.arglock:
                if cfunc.argtypes is None:
                    cfunc.argtypes = [
                        lib_importer.task_handle, ctypes_byte_str, ctypes.POINTER(ctypes.c_int32)]

        error_code = cfunc(self._handle, self._name, ctypes.byref(val))
        check_for_error(error_code)
        return val.value

    @property
    def co_output_state(self):
        """
        Indicates the current state of the output terminal of the counter.
        """
        val = ctypes.c_int32()
        cfunc = lib_importer.windll.ArtDAQ_GetCOOutputState
        if cfunc.argtypes is None:
            with cfunc.arglock:
                if cfunc.argtypes is None:
                    cfunc.argtypes = [
                        lib_importer.task_handle, ctypes_byte_str, ctypes.POINTER(ctypes.c_int32)]

        error_code = cfunc(self._handle, self._name, ctypes.byref(val))
        check_for_error(error_code)
        return ToggleIdleState(val.value)

    @property
    def co_enable_initial_delay_on_retrigger(self):
        """
        Specifies whether the B input signal needs to be inverted.
        """
        val = ctypes.c_int32()
        cfunc = lib_importer.windll.ArtDAQ_GetCOEnableInitialDelayOnRetrigger
        if cfunc.argtypes is None:
            with cfunc.arglock:
                if cfunc.argtypes is None:
                    cfunc.argtypes = [
                        lib_importer.task_handle, ctypes_byte_str, ctypes.POINTER(ctypes.c_int32)]

        error_code = cfunc(self._handle, self._name, ctypes.byref(val))
        check_for_error(error_code)
        return val.value

    @co_enable_initial_delay_on_retrigger.setter
    def co_enable_initial_delay_on_retrigger(self, val):
        cfunc = lib_importer.windll.ArtDAQ_SetCOEnableInitialDelayOnRetrigger
        if cfunc.argtypes is None:
            with cfunc.arglock:
                if cfunc.argtypes is None:
                    cfunc.argtypes = [
                        lib_importer.task_handle, ctypes_byte_str, ctypes.c_uint32]

        error_code = cfunc(
            self._handle, self._name, val)
        check_for_error(error_code)














































    @property
    def co_output_type(self):
        """
        :class:`artdaq.constants.UsageTypeCO`: Indicates how to define
            pulses generated on the channel.
        """
        return 0