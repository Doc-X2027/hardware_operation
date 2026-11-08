from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import ctypes
import numpy
import struct

from artdaq._lib import (
    lib_importer, wrapped_ndpointer, enum_bitfield_to_list, ctypes_byte_str,
    c_bool32)
from artdaq.errors import (check_for_error, is_string_buffer_too_small, is_array_buffer_too_small)
from artdaq.constants import (AcquisitionType)



class Device(object):
    """
    Represents a DAQ device.
    """

    def __init__(self, task_handle):
        """
        Args:
            name (str): Specifies the name of the device.
        """
        self._handle = task_handle


    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self._name == other._name
        return False

    def __hash__(self):
        return hash(self._name)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return 'Device(name={0})'.format(self._name)

    @property
    def name(self):
        """
        str: Specifies the name of this device.
        """
        return self._name

    # region Physical Channel Collections

    @staticmethod
    def get_double_type_attribute(self, device_name, attribute_id):
        """
        """
        cfunc = lib_importer.windll.ArtDAQ_GetDeviceAttribute
        if cfunc.argtypes is None:
            with cfunc.arglock:
                if cfunc.argtypes is None:
                    cfunc.argtypes = [ctypes_byte_str, ctypes.c_uint, ctypes.c_char_p,
                                      self._handle]

        temp_size = 8
        while True:
            val = ctypes.create_string_buffer(temp_size)
            size_or_code = cfunc(
                device_name, attribute_id, val, self._handle)

            if is_string_buffer_too_small(size_or_code):
                # Buffer size must have changed between calls; check again.
                temp_size = 0
            elif size_or_code > 0 and temp_size == 0:
                # Buffer size obtained, use to retrieve data.
                temp_size = size_or_code
            else:
                break

        check_for_error(size_or_code)
        data = numpy.frombuffer(val, dtype=ctypes.c_double, count=-1, offset=0)
        return data[0]

    @staticmethod
    def get_int_type_attribute(self, device_name, attribute_id):
        cfunc = lib_importer.windll.ArtDAQ_GetDeviceAttribute
        if cfunc.argtypes is None:
            with cfunc.arglock:
                if cfunc.argtypes is None:
                    cfunc.argtypes = [ctypes_byte_str, ctypes.c_uint, ctypes.c_char_p,
                                      self._handle]

        temp_size = 256
        while True:
            val = ctypes.create_string_buffer(temp_size)
            size_or_code = cfunc(
                device_name, attribute_id, val, self._handle)

            if is_string_buffer_too_small(size_or_code):
                # Buffer size must have changed between calls; check again.
                temp_size = 0
            elif size_or_code > 0 and temp_size == 0:
                # Buffer size obtained, use to retrieve data.
                temp_size = size_or_code
            else:
                break

        check_for_error(size_or_code)
        int_data = int.from_bytes(val, byteorder='little', signed=True)

        return int_data

    @staticmethod
    def get_string_type_attribute(self, device_name, attribute_id):
        cfunc = lib_importer.windll.ArtDAQ_GetDeviceAttribute
        if cfunc.argtypes is None:
            with cfunc.arglock:
                if cfunc.argtypes is None:
                    cfunc.argtypes = [ctypes_byte_str, ctypes.c_uint, ctypes.c_char_p,
                                      self._handle]

        temp_size = 256
        while True:
            val = ctypes.create_string_buffer(temp_size)
            size_or_code = cfunc(
                device_name, attribute_id, val, self._handle)

            if is_string_buffer_too_small(size_or_code):
                # Buffer size must have changed between calls; check again.
                temp_size = 0
            elif size_or_code > 0 and temp_size == 0:
                # Buffer size obtained, use to retrieve data.
                temp_size = size_or_code
            else:
                break

        check_for_error(size_or_code)
        string_data = val.value.decode('ascii')

        return string_data



    def product_type(self, device_name):
        """
        List[nidaqmx.system._collections.PhysicalChannelCollection]:
            Indicates a collection that contains all the analog input
            physical channels available on the device.such as PCIe9870
        """
        return self.get_string_type_attribute(self,device_name, 0x0631)

    def serial_num(self, device_name):
        """
         int: Indicates the serial number of the device. This value is zero if the device does not have a serial number.
        """
        return self.get_int_type_attribute(device_name, 0x0632)

    def ai_physical_chans(self, device_name):
        """
        Indicates the number of the analog input physical channels available on the device.
        """
        return self.get_int_type_attribute(self, device_name, 0x0231E)

    def ai_max_single_chan_rate(self, device_name):
        """
               Indicates the max single chan rate of the analog input physical channels available on the device.
               """
        return self.get_double_type_attribute(self, device_name, 0x298C)

    def ai_max_multi_chan_rate(self, device_name):
        """
               Indicates the min multi chans rate of the analog input physical channels available on the device.
               """
        return self.get_double_type_attribute(self, device_name, 0x298D)

    def ai_min_rate(self, device_name):
        return self.get_double_type_attribute(self, device_name, 0x298E)

    def ai_sample_modes(self, device_name):
        cfunc = lib_importer.windll.ArtDAQ_GetDeviceAttribute
        if cfunc.argtypes is None:
            with cfunc.arglock:
                if cfunc.argtypes is None:
                    cfunc.argtypes = [ctypes_byte_str, ctypes.c_uint, ctypes.c_char_p,
                                      self._handle]

        temp_size = 16
        while True:
            val = ctypes.create_string_buffer(temp_size)
            size_or_code = cfunc(
                device_name, 0x2FDC, val, self._handle)

            if is_string_buffer_too_small(size_or_code):
                # Buffer size must have changed between calls; check again.
                temp_size = 0
            elif size_or_code > 0 and temp_size == 0:
                # Buffer size obtained, use to retrieve data.
                temp_size = size_or_code
            else:
                break

        check_for_error(size_or_code)
        listData = []
        for i in range(0,4):
            data= int.from_bytes(val[i*4:i*4+4], byteorder='little', signed=True)
            if data != 0:
               listData.insert(len(listData), AcquisitionType(data))
        return listData

    def ao_physicalChan(self, device_name):
        return self.get_int_type_attribute(self, device_name, 0x231F)

    def ao_max_rate(self, device_name):
        return self.get_double_type_attribute(self, device_name, 0x2997)

    def ao_min_rate(self, device_name):
        return self.get_double_type_attribute(self, device_name, 0x2998)

    def di_max_rate(self, device_name):
        return self.get_double_type_attribute(self, device_name, 0x2999)

    def do_max_rate(self, device_name):
        return self.get_double_type_attribute(self, device_name, 0x299A)

    def frequence_output_timebase(self, device_name):
        val = ctypes.c_double()
        cfunc = lib_importer.windll.ArtDAQ_GetFrequenceOutputTimebase
        if cfunc.argtypes is None:
            with cfunc.arglock:
                cfunc.argtypes = [ctypes_byte_str, ctypes.POINTER(ctypes.c_double)]
        error_code = cfunc(device_name, ctypes.byref(val))
        check_for_error(error_code)
        return val.value


    def frequence_output_timebase_div(self, device_name, val):
        cfunc = lib_importer.windll.ArtDAQ_SetFrequenceOutputTimebaseDiv
        if cfunc.argtypes is None:
            with cfunc.arglock:
                cfunc.argtypes = [ctypes_byte_str, ctypes.c_uint32]
        error_code = cfunc(device_name, val)
        check_for_error(error_code)

    def reset(self, device_name):
        cfunc = lib_importer.windll.ArtDAQ_ResetDevice
        if cfunc.argtypes is None:
            with cfunc.arglock:
                cfunc.argtypes = [ctypes_byte_str]
        error_code = cfunc(device_name)
        check_for_error(error_code)

    def Self_test(self, device_name):
        cfunc = lib_importer.windll.ArtDAQ_SelfTestDevice
        if cfunc.argtypes is None:
            with cfunc.arglock:
                cfunc.argtypes = [ctypes_byte_str]
        error_code = cfunc(device_name)
        check_for_error(error_code)


    def digital_power_up_states(self, device_name, channe_nanmes, state, arraysize):

        cfunc = lib_importer.windll.ArtDAQ_GetDigitalPowerUpStates
        if cfunc.argtypes is None:
            with cfunc.arglock:
                cfunc.argtypes = [ctypes_byte_str, ctypes_byte_str,
                                  wrapped_ndpointer(dtype=numpy.int32, flags=('C', 'W')), ctypes.c_uint32]
        error_code = cfunc(device_name, channe_nanmes, state, arraysize)
        check_for_error(error_code)

    def set_digital_power_up_states(self, device_name, channe_nanmes, state):

        cfunc = lib_importer.windll.ArtDAQ_SetDigitalPowerUpStates
        if cfunc.argtypes is None:
            with cfunc.arglock:
                cfunc.argtypes = [ctypes_byte_str, ctypes_byte_str,
                                  wrapped_ndpointer(dtype=numpy.int32, flags=('C', 'W'))]
        error_code = cfunc(device_name, channe_nanmes, state)
        check_for_error(error_code)

    def get_power_output_states(self, device_name, outputEnable,):

        cfunc = lib_importer.windll.ArtDAQ_Get5VPowerOutputStates
        if cfunc.argtypes is None:
            with cfunc.arglock:
                cfunc.argtypes = [ctypes_byte_str, ctypes.POINTER(ctypes.c_int)]
        error_code = cfunc(device_name, ctypes.byref(outputEnable))
        check_for_error(error_code)

    def set_power_output_states(self, device_name, outputEnable):

        cfunc = lib_importer.windll.ArtDAQ_Get5VPowerOutputStates
        if cfunc.argtypes is None:
            with cfunc.arglock:
                cfunc.argtypes = [ctypes_byte_str, ctypes.c_int]
        error_code = cfunc(device_name, outputEnable)
        check_for_error(error_code)


    def get_power_power_up_states(self, device_name, outputEnable):

        cfunc = lib_importer.windll.ArtDAQ_Get5VPowerPowerUpStates
        if cfunc.argtypes is None:
            with cfunc.arglock:
                cfunc.argtypes = [ctypes_byte_str, ctypes.POINTER(ctypes.c_int)]
        error_code = cfunc(device_name, ctypes.byref(outputEnable))
        check_for_error(error_code)

    def set_power_power_up_states(self, device_name, outputEnable):

        cfunc = lib_importer.windll.ArtDAQ_Set5VPowerPowerUpStates
        if cfunc.argtypes is None:
            with cfunc.arglock:
                cfunc.argtypes = [ctypes_byte_str, ctypes.c_int]
        error_code = cfunc(device_name, outputEnable)
        check_for_error(error_code)

    def get_device_list(dev_class, buffer, buffer_size, dev_count):

        cfunc = lib_importer.windll.DMCSCSL_GetDeviceList

        if cfunc.argtypes is None:
            with cfunc.arglock:
                if cfunc.argtypes is None:
                    cfunc.argtypes = [
                        ctypes.c_uint32, ctypes.c_void_p, ctypes.c_int32, ctypes.POINTER(ctypes.c_int32)]

        error_code = cfunc(dev_class, buffer, buffer_size, ctypes.byref(dev_count))
        check_for_error(error_code)

    def rename_device(device_name, new_name):

        cfunc = lib_importer.windll.DMCSCSL_RenameDevice

        if cfunc.argtypes is None:
            with cfunc.arglock:
                if cfunc.argtypes is None:
                    cfunc.argtypes = [wrapped_ndpointer(dtype=numpy.char, flags=('C', 'W')),
                                      wrapped_ndpointer(dtype=numpy.char, flags=('C', 'W'))]
        error_code = cfunc(device_name, new_name)
        check_for_error(error_code)



    # endregion
