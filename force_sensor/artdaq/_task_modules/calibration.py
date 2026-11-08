from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import ctypes

from artdaq._lib import (lib_importer, ctypes_byte_str)
from artdaq.errors import (check_for_error)


class Calibration(object):
    """
    Represents the pause trigger configurations for a DAQ task.
    """
    def __init__(self, task_handle):
        self._handle = task_handle

    def self_cal(self, device_name):
        cfunc = lib_importer.windll.ArtDAQ_SelfCal
        if cfunc.argtypes is None:
            with cfunc.arglock:
                if cfunc.argtypes is None:
                    cfunc.argtypes = [ctypes_byte_str]
        error_code = cfunc(device_name)
        check_for_error(error_code)

    def get_char_calinfo_attributeF64(self, device_name, attribute, value):
        cfunc = lib_importer.windll.ArtDAQ_GetCharCalInfoAttributeF64
        if cfunc.argtypes is None:
            with cfunc.arglock:
                if cfunc.argtypes is None:
                    cfunc.argtypes = [ctypes_byte_str, ctypes.c_int32, ctypes.POINTER(ctypes.c_double)]
        error_code = cfunc(device_name, attribute, ctypes.byref(value))
        check_for_error(error_code)

    def set_char_calinfo_attributeF64(self, device_name, attribute, value):
        cfunc = lib_importer.windll.ArtDAQ_SetChanCalInfoAttributeF64
        if cfunc.argtypes is None:
            with cfunc.arglock:
                if cfunc.argtypes is None:
                    cfunc.argtypes = [ctypes_byte_str, ctypes.c_int32, ctypes.c_double]
        error_code = cfunc(device_name, attribute, value)
        check_for_error(error_code)


    def reset_char_calinfo_attribute(self, device_name, attribute):
        cfunc = lib_importer.windll.ArtDAQ_ResetChanCalInfoAttribute
        if cfunc.argtypes is None:
            with cfunc.arglock:
                if cfunc.argtypes is None:
                    cfunc.argtypes = [ctypes_byte_str, ctypes.c_int32]
        error_code = cfunc(device_name, attribute)
        check_for_error(error_code)
    def get_AI_cal_offset_and_gain(self, device_name, channel, min_val, max_val,
                                   sample_clock, offset, code_width):
        cfunc = lib_importer.windll.ArtDAQ_GetAICalOffsetAndGain
        if cfunc.argtypes is None:
            with cfunc.arglock:
                cfunc.argtypes = [ctypes_byte_str, ctypes.c_uint, ctypes.c_double,
                                  ctypes.c_double, ctypes.c_double, ctypes.POINTER(ctypes.c_double),
                                  ctypes.POINTER(ctypes.c_double)]
        error_code = cfunc(device_name, channel, min_val, max_val,
                           sample_clock, ctypes.byref(offset), ctypes.byref(code_width))
        check_for_error(error_code)

    def get_AO_cal_offset_and_gain(self, device_name, channel, min_val, max_val,
                                   sample_clock, offset, code_width):
        cfunc = lib_importer.windll.ArtDAQ_GetAOCalOffsetAndGain
        if cfunc.argtypes is None:
            with cfunc.arglock:
                cfunc.argtypes = [ctypes_byte_str, ctypes.c_uint, ctypes.c_double,
                                  ctypes.c_double, ctypes.c_double, ctypes.POINTER(ctypes.c_double),
                                  ctypes.POINTER(ctypes.c_double)]

        error_code = cfunc(device_name, channel, min_val, max_val,
                           sample_clock, ctypes.byref(offset), ctypes.byref(code_width))
        check_for_error(error_code)

    def perform_bridge_offset_nulling_cal(self, channel=""):
        cfunc = lib_importer.windll.ArtDAQ_PerformBridgeOffsetNullingCal
        if cfunc.argtypes is None:
            with cfunc.arglock:
                cfunc.argtypes = [lib_importer.task_handle, ctypes_byte_str]
        error_code = cfunc(self._handle, channel)
        check_for_error(error_code)

    def perform_strain_shunt_cal(self, channel, shunt_resistor_val, shunt_resistor_location,
                                 skip_unsupported_channels):
        cfunc = lib_importer.windll.ArtDAQ_PerformStrainShuntCal
        if cfunc.argtypes is None:
            with cfunc.arglock:
                cfunc.argtypes = [lib_importer.task_handle, ctypes_byte_str, ctypes.c_double,
                                  ctypes.c_int, ctypes.c_bool]
        error_code = cfunc(self._handle, channel, shunt_resistor_val, shunt_resistor_location,
                                 skip_unsupported_channels)
        check_for_error(error_code)

    def perform_bridge_shunt_cal(self, channel, shunt_resistor_val, shunt_resistor_location,
                                 bridge_resistance, skip_unsupported_channels):
        cfunc = lib_importer.windll.ArtDAQ_PerformBridgeShuntCal
        if cfunc.argtypes is None:
            with cfunc.arglock:
                cfunc.argtypes = [lib_importer.task_handle, ctypes_byte_str,
                                  ctypes.c_double, ctypes.c_int32, ctypes.c_double, ctypes.c_bool]
        error_code = cfunc(self._handle, channel, shunt_resistor_val, shunt_resistor_location,
                                 bridge_resistance, skip_unsupported_channels)
        check_for_error(error_code)

