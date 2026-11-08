from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import ctypes
from artdaq._lib import (lib_importer, ctypes_byte_str)
from artdaq.errors import check_for_error
from artdaq._task_modules.channels.channel import Channel
from artdaq._task_modules.channels.ai_channel import AIChannel
from artdaq._task_modules.channel_collection import ChannelCollection
from artdaq.utils import unflatten_channel_string
from artdaq.constants import (Coupling, ExcitationSource, TerminalConfiguration, VoltageUnits, ChannelType ,CurrentUnits ,
                              CurrentShuntResistorLocation, ThermocoupleUnits, ThermocoupleType, CJCSource, ResistanceUnits,
                              RtdType, ResistanceConfiguration, ExcitationSource, StrainUnits, StrainGageBridgeType,
                              BridgeUnits, BridgeConfiguration)


class AIChannelCollection(ChannelCollection):
    """
    Contains the collection of analog input channels for a DAQ Task.
    """
    def __init__(self, task_handle):
        super(AIChannelCollection, self).__init__(task_handle)

    def _create_chan(self, physical_channel, name_to_assign_to_channel=''):
        """
        Creates and returns an AIChannel object.

        Args:
            physical_channel (str): Specifies the names of the physical
                channels to use to create virtual channels.
            name_to_assign_to_channel (Optional[str]): Specifies a name to
                assign to the virtual channel this method creates.
        Returns:
            artdaq._task_modules.channels.ai_channel.AIChannel: 
            
            Specifies the newly created AIChannel object.
        """
        if name_to_assign_to_channel:
            num_channels = len(unflatten_channel_string(physical_channel))

            if num_channels > 1:
                name = '{0}0:{1}'.format(
                    name_to_assign_to_channel, num_channels-1)
            else:
                name = name_to_assign_to_channel
        else:
            name = physical_channel

        return AIChannel(self._handle, name)

    def add_ai_voltage_chan(
            self, physical_channel, name_to_assign_to_channel="",
            terminal_config=TerminalConfiguration.DEFAULT, min_val=-10,
            max_val=10, units=VoltageUnits.VOLTS, custom_scale_name=""):
        """
        Creates channel(s) to measure voltage. If the measurement
        requires the use of internal excitation or you need excitation
        to scale the voltage, use the AI Custom Voltage with Excitation
        instance of this function.

        Args:
            physical_channel (str): Specifies the names of the physical
                channels to use to create virtual channels. The DAQ
                physical channel constant lists all physical channels on
                devices and modules installed in the system.
            name_to_assign_to_channel (Optional[str]): Specifies a name
                to assign to the virtual channel this function creates.
                If you do not specify a value for this input, ArtDAQ
                uses the physical channel name as the virtual channel
                name.
            terminal_config (Optional[artdaq.constants.TerminalConfiguration]):
                Specifies the input terminal configuration for the
                channel.
            min_val (Optional[float]): Specifies in **units** the
                minimum value you expect to measure.
            max_val (Optional[float]): Specifies in **units** the
                maximum value you expect to measure.
            units (Optional[artdaq.constants.VoltageUnits]): Specifies
                the units to use to return voltage measurements.
            custom_scale_name (Optional[str]): Specifies the name of a
                custom scale for the channel. If you want the channel to
                use a custom scale, specify the name of the custom scale
                to this input and set **units** to
                **FROM_CUSTOM_SCALE**.
        Returns:
            artdaq._task_modules.channels.ai_channel.AIChannel:

            Indicates the newly created channel object.
        """
        cfunc = lib_importer.windll.ArtDAQ_CreateAIVoltageChan
        if cfunc.argtypes is None:
            with cfunc.arglock:
                if cfunc.argtypes is None:
                    cfunc.argtypes = [
                        lib_importer.task_handle, ctypes_byte_str,
                        ctypes_byte_str, ctypes.c_int, ctypes.c_double,
                        ctypes.c_double, ctypes.c_int, ctypes_byte_str]

        error_code = cfunc(
            self._handle, physical_channel, name_to_assign_to_channel,
            terminal_config.value, min_val, max_val, units.value,
            custom_scale_name)
        check_for_error(error_code)
        return self._create_chan(physical_channel, name_to_assign_to_channel)

    def add_ai_voltage_iepe_chan(
            self, physical_channel, name_to_assign_to_channel="",
            terminal_config=TerminalConfiguration.DEFAULT, coupling=Coupling.DC, min_val=-5.0,
            max_val=5.0,
            current_excit_source=ExcitationSource.INTERNAL,
            current_excit_val=0.004):
        """
        Creates channel(s) that use an IEPE velocity sensor to measure
        velocity.

        Args:
            physical_channel (str): Specifies the names of the physical
                channels to use to create virtual channels. The DAQ
                physical channel constant lists all physical channels on
                devices and modules installed in the system.
            name_to_assign_to_channel (Optional[str]): Specifies a name
                to assign to the virtual channel this function creates.
                If you do not specify a value for this input, ArtDAQ
                uses the physical channel name as the virtual channel
                name.
            terminal_config (Optional[artdaq.constants.TerminalConfiguration]):
                Specifies the input terminal configuration for the
                channel.
            coupling: (Optional[artdaq.constants.Coupling])couple mode.
            min_val (Optional[float]): Specifies in **units** the
                minimum value you expect to measure.
            max_val (Optional[float]): Specifies in **units** the
                maximum value you expect to measure.
            current_excit_source (Optional[artdaq.constants.ExcitationSource]):
                Specifies the source of excitation.
            current_excit_val (Optional[float]): Specifies in amperes
                the amount of excitation to supply to the sensor. Refer
                to the sensor documentation to determine this value.
        Returns:
            artdaq._task_modules.channels.ai_channel.AIChannel:
            Indicates the newly created channel object.
        """
        cfunc = lib_importer.windll.ArtDAQ_CreateAIVoltageIEPEChan
        if cfunc.argtypes is None:
            with cfunc.arglock:
                if cfunc.argtypes is None:
                    cfunc.argtypes = [
                        lib_importer.task_handle, ctypes_byte_str,
                        ctypes_byte_str, ctypes.c_int, ctypes.c_int,
                        ctypes.c_double, ctypes.c_double,
                        ctypes.c_int, ctypes.c_double]

        error_code = cfunc(
            self._handle, physical_channel, name_to_assign_to_channel,
            terminal_config.value, coupling.value, min_val, max_val, current_excit_source.value,
            current_excit_val)
        check_for_error(error_code)
        return self._create_chan(physical_channel, name_to_assign_to_channel)

    def add_ai_current_chan(
            self, physical_channel, name_to_assign_to_channel="",
            terminal_config=TerminalConfiguration.DEFAULT, coupling=Coupling.DC, min_val=-5.0,
            max_val=5.0, units=CurrentUnits.AMPS,
            shunt_resistor_location=CurrentShuntResistorLocation.INTERNAL,
            ext_shunt_resistor_val=0.004, custom_scale_name=""):
        """
        Creates channel(s) that use an IEPE velocity sensor to measure
        velocity.

        Args:
            physical_channel (str): Specifies the names of the physical
                channels to use to create virtual channels. The DAQ
                physical channel constant lists all physical channels on
                devices and modules installed in the system.
            name_to_assign_to_channel (Optional[str]): Specifies a name
                to assign to the virtual channel this function creates.
                If you do not specify a value for this input, ArtDAQ
                uses the physical channel name as the virtual channel
                name.
            terminal_config (Optional[artdaq.constants.TerminalConfiguration]):
                Specifies the input terminal configuration for the
                channel.
            coupling: (Optional[artdaq.constants.Coupling])couple mode.
            min_val (Optional[float]): Specifies in **units** the
                minimum value you expect to measure.
            max_val (Optional[float]): Specifies in **units** the
                maximum value you expect to measure.
            units (Optional[artdaq.constants.CurrentUnits]): Specifies
                the units to use to return current measurements.
            shunt_resistor_location (Optional[artdaq.constants.CurrentShuntResistorLocation]): Specifies in  shunt resistor location.
            ext_shunt_resistor_val (Optional[float]): Specifies in external shunt resistor
                this value.
            custom_scale_name (Optional[str]): Specifies the name of a
                custom scale for the channel. If you want the channel to
                use a custom scale, specify the name of the custom scale
                to this input and set **units** to
                **FROM_CUSTOM_SCALE**.
        Returns:
            artdaq._task_modules.channels.ai_channel.AIChannel:
            Indicates the newly created channel object.
        """
        cfunc = lib_importer.windll.ArtDAQ_CreateAICurrentChan
        if cfunc.argtypes is None:
            with cfunc.arglock:
                if cfunc.argtypes is None:
                    cfunc.argtypes = [
                        lib_importer.task_handle, ctypes_byte_str,
                        ctypes_byte_str, ctypes.c_int,
                        ctypes.c_double, ctypes.c_double, ctypes.c_int,
                        ctypes.c_int, ctypes.c_double, ctypes_byte_str]

        error_code = cfunc(
            self._handle, physical_channel, name_to_assign_to_channel,
            terminal_config.value, coupling.value, min_val, max_val, units.value,
            shunt_resistor_location.value, ext_shunt_resistor_val, custom_scale_name)
        check_for_error(error_code)
        return self._create_chan(physical_channel, name_to_assign_to_channel)

    def add_ai_thermocouple_chan(
            self, physical_channel, name_to_assign_to_channel="",
            min_val=0.0, max_val=100.0, units=ThermocoupleUnits.DEGC,
            thermo_couple_type=ThermocoupleType.J_TYPE_TC,
            cjc_source=CJCSource.BUILTIN, cjc_val=25.0, cjc_channel=""):
        """
        Creates channel(s) that use an IEPE velocity sensor to measure
        velocity.

        Args:
            physical_channel (str): Specifies the names of the physical
                channels to use to create virtual channels. The DAQ
                physical channel constant lists all physical channels on
                devices and modules installed in the system.
            name_to_assign_to_channel (Optional[str]): Specifies a name
                to assign to the virtual channel this function creates.
                If you do not specify a value for this input, ArtDAQ
                uses the physical channel name as the virtual channel
                name.
            min_val (Optional[float]): Specifies in **units** the
                minimum value you expect to measure.
            max_val (Optional[float]): Specifies in **units** the
                maximum value you expect to measure.
            units (Optional[artdaq.constants.ThermocoupleUnits]): Specifies the units to use to return temperature
                measurements from the channel.
            thermo_couple_type (Optional[artdaq.constants.ThermocoupleType]): Specifies the type of thermocouple connected to the channel.
                Thermocouple types differ in composition and measurement range.
            cjc_source (Optional[artdaq.constants.ThermocoupleType]): Indicates the source of cold-junction compensation.
            cjc_val (Optional[float]): Specifies the temperature of the cold junction if CJC Source is CONSTVAL.
                Specify this value in the units of the measurement.
            cjc_channel (str): Indicates the channel that acquires the temperature of the cold junction if CJC Source is CHAN. If the channel is a temperature channel, ArtDAQ acquires the temperature in the correct units. Other channel types, such as a resistance channel with a custom sensor,
                must use a custom scale to scale values to degrees Celsius.
        Returns:
            artdaq._task_modules.channels.ai_channel.AIChannel:
            Indicates the newly created channel object.
        """
        cfunc = lib_importer.windll.ArtDAQ_CreateAIThrmcplChan
        if cfunc.argtypes is None:
            with cfunc.arglock:
                if cfunc.argtypes is None:
                    cfunc.argtypes = [
                        lib_importer.task_handle, ctypes_byte_str,
                        ctypes_byte_str, ctypes.c_double, ctypes.c_double, ctypes.c_int,
                        ctypes.c_int, ctypes.c_int, ctypes.c_double, ctypes_byte_str]

        error_code = cfunc(
            self._handle, physical_channel, name_to_assign_to_channel,
            min_val, max_val, units.value, thermo_couple_type.value, cjc_source.value,
            cjc_val, cjc_channel)
        check_for_error(error_code)
        return self._create_chan(physical_channel, name_to_assign_to_channel)


    def add_ai_rtd_chan(
            self, physical_channel, name_to_assign_to_channel="",
            min_val=0.0, max_val=100.0, units=ThermocoupleUnits.DEGC,
            rtd_type=RtdType.PT3750, resistance_config=ResistanceConfiguration.FOUR_WIRE,
            current_excit_Source=ExcitationSource.INTERNAL, current_excitVal=0.004, r0=100.0
            ):
        """
        Creates channel(s) that use an IEPE velocity sensor to measure
        velocity.

        Args:
            physical_channel (str): Specifies the names of the physical
                channels to use to create virtual channels. The DAQ
                physical channel constant lists all physical channels on
                devices and modules installed in the system.
            name_to_assign_to_channel (Optional[str]): Specifies a name
                to assign to the virtual channel this function creates.
                If you do not specify a value for this input, ArtDAQ
                uses the physical channel name as the virtual channel
                name.
            min_val (Optional[float]): Specifies in **units** the
                minimum value you expect to measure.
            max_val (Optional[float]): Specifies in **units** the
                maximum value you expect to measure.
            units (Optional[artdaq.constants.ThermocoupleUnits]): Specifies the units to use to return temperature measurements from the channel.
            rtd_type (Optional[artdaq.constants.RtdType]): Specifies the type of RTD connected to the channel.
            resistance_config (Optional[artdaq.constants.ResistanceConfiguration]): Specifies the resistance configuration for the channel. ArtDAQ uses this value for any resistance-based measurements,
                including temperature measurement using a thermistor or RTD.
            current_excit_Source (Optional[artdaq.constants.ExcitationSource]): Specifies the source of excitation.
            current_excitVal (Optional[float]):Specifies the amount of excitation that the sensor requires. If Voltage or Current is  ArtDAQ_Val_Voltage, this value is in volts.
                If Voltage or Current is  ArtDAQ_Val_Current, this value is in amperes.
            r0(Optional[float]):The resistance of a resistor.
        Returns:
            artdaq._task_modules.channels.ai_channel.AIChannel:
            Indicates the newly created channel object.
        """
        cfunc = lib_importer.windll.ArtDAQ_CreateAIRTDChan
        if cfunc.argtypes is None:
            with cfunc.arglock:
                if cfunc.argtypes is None:
                    cfunc.argtypes = [
                        lib_importer.task_handle, ctypes_byte_str,
                        ctypes_byte_str, ctypes.c_double, ctypes.c_double, ctypes.c_int,
                        ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_double, ctypes.c_double]

        error_code = cfunc(
            self._handle, physical_channel, name_to_assign_to_channel,
            min_val, max_val, units.value, rtd_type.value, resistance_config.value, current_excit_Source.value, current_excitVal, r0)
        check_for_error(error_code)
        return self._create_chan(physical_channel, name_to_assign_to_channel)


    def add_ai_thrmstr_chan_iex(
            self, physical_channel, name_to_assign_to_channel="",
            min_val=-5.0, max_val=5.0, units=ThermocoupleUnits.DEGC,
            resistance_config=ResistanceConfiguration.TWO_WIRE,
            current_excit_Source=ExcitationSource.INTERNAL, current_excitVal=1.00, a=1.00,
            b=1.00, c=1.00):
        """
        Creates channel(s) that use an IEPE velocity sensor to measure
        velocity.

        Args:
            physical_channel (str): Specifies the names of the physical
                channels to use to create virtual channels. The DAQ
                physical channel constant lists all physical channels on
                devices and modules installed in the system.
            name_to_assign_to_channel (Optional[str]): Specifies a name
                to assign to the virtual channel this function creates.
                If you do not specify a value for this input, ArtDAQ
                uses the physical channel name as the virtual channel
                name.
            min_val (Optional[float]): Specifies in **units** the
                minimum value you expect to measure.
            max_val (Optional[float]): Specifies in **units** the
                maximum value you expect to measure.
            units (Optional[artdaq.constants.ThermocoupleUnits]): Specifies the units to use to return temperature measurements from the channel.
            resistance_config (Optional[artdaq.constants.ResistanceConfiguration]): Specifies the resistance configuration for the channel.
                ArtDAQ uses this value for any resistance-based measurements,
                including temperature measurement using a thermistor or RTD.
            current_excit_Source (Optional[artdaq.constants.ExcitationSource]): Specifies the source of excitation.
            current_excitVal (Optional[float]):Specifies the amount of excitation that the sensor requires.
                If Voltage or Current is  ArtDAQ_Val_Voltage, this value is in volts.
                If Voltage or Current is  ArtDAQ_Val_Current, this value is in amperes.
            a(Optional[float]):Specifies the 'A' constant of the Steinhart-Hart thermistor equation.
            b(Optional[float]):Specifies the 'B' constant of the Steinhart-Hart thermistor equation.
            c(Optional[float]):Specifies the 'C' constant of the Steinhart-Hart thermistor equation.
        Returns:
            artdaq._task_modules.channels.ai_channel.AIChannel:
            Indicates the newly created channel object.
        """
        cfunc = lib_importer.windll.ArtDAQ_CreateAIThrmstrChanIex
        if cfunc.argtypes is None:
            with cfunc.arglock:
                if cfunc.argtypes is None:
                    cfunc.argtypes = [
                        lib_importer.task_handle, ctypes_byte_str,
                        ctypes_byte_str, ctypes.c_double, ctypes.c_double, ctypes.c_int,
                        ctypes.c_int, ctypes.c_int, ctypes.c_double, ctypes.c_double, ctypes.c_double, ctypes.c_double]

        error_code = cfunc(
            self._handle, physical_channel, name_to_assign_to_channel,
            min_val, max_val, units.value,  resistance_config.value, current_excit_Source.value, current_excitVal, a, b, c)
        check_for_error(error_code)
        return self._create_chan(physical_channel, name_to_assign_to_channel)


    def add_ai_thrmstr_chan_vex(
            self, physical_channel, name_to_assign_to_channel="",
            min_val=-5.0, max_val=5.0, units=ThermocoupleUnits.DEGC,
            resistance_config=ResistanceConfiguration.TWO_WIRE,
            voltage_excit_Source=ExcitationSource.INTERNAL, voltage_excit_Val=1.00, a=1.00,
            b=1.00, c=1.00, r1=1.00):
        """
        Creates channel(s) that use an IEPE velocity sensor to measure
        velocity.

        Args:
            physical_channel (str): Specifies the names of the physical
                channels to use to create virtual channels. The DAQ
                physical channel constant lists all physical channels on
                devices and modules installed in the system.
            name_to_assign_to_channel (Optional[str]): Specifies a name
                to assign to the virtual channel this function creates.
                If you do not specify a value for this input, ArtDAQ
                uses the physical channel name as the virtual channel
                name.
            min_val (Optional[float]): Specifies in **units** the
                minimum value you expect to measure.
            max_val (Optional[float]): Specifies in **units** the
                maximum value you expect to measure.
            units (Optional[artdaq.constants.ThermocoupleUnits]): Specifies the units to use to return temperature measurements from the channel.
            resistance_config (Optional[artdaq.constants.ResistanceConfiguration]): Specifies the resistance configuration for the channel.
                ArtDAQ uses this value for any resistance-based measurements,
                including temperature measurement using a thermistor or RTD.
            voltage_excit_Source (Optional[artdaq.constants.ExcitationSource]): Specifies the source of excitation.
            voltage_excit_Val (Optional[float]):Specifies the amount of excitation that the sensor requires.
                If Voltage or Current is  ArtDAQ_Val_Voltage, this value is in volts.
                If Voltage or Current is  ArtDAQ_Val_Current, this value is in amperes.
            a(Optional[float]):Specifies the 'A' constant of the Steinhart-Hart thermistor equation.
            b(Optional[float]):Specifies the 'B' constant of the Steinhart-Hart thermistor equation.
            c(Optional[float]):Specifies the 'C' constant of the Steinhart-Hart thermistor equation.
            r1(Optional[float]):Specifies in ohms the value of the reference resistor for the thermistor if you use voltage excitation.
                ArtDAQ ignores this value for current excitation.
        Returns:
            artdaq._task_modules.channels.ai_channel.AIChannel:
            Indicates the newly created channel object.
        """
        cfunc = lib_importer.windll.ArtDAQ_CreateAIThrmstrChanVex
        if cfunc.argtypes is None:
            with cfunc.arglock:
                if cfunc.argtypes is None:
                    cfunc.argtypes = [
                        lib_importer.task_handle, ctypes_byte_str,
                        ctypes_byte_str, ctypes.c_double, ctypes.c_double, ctypes.c_int,
                        ctypes.c_int, ctypes.c_int, ctypes.c_double, ctypes.c_double, ctypes.c_double, ctypes.c_double, ctypes.c_double]

        error_code = cfunc(
            self._handle, physical_channel, name_to_assign_to_channel,
            min_val, max_val, units.value,  resistance_config.value, voltage_excit_Source.value, voltage_excit_Val, a, b, c, r1)
        check_for_error(error_code)
        return self._create_chan(physical_channel, name_to_assign_to_channel)


    def add_ai_resistance_chan(
            self, physical_channel, name_to_assign_to_channel="",
            min_val=-5.0, max_val=5.0, units=ResistanceUnits.OHMS,
            resistance_config=ResistanceConfiguration.TWO_WIRE,
            current_excit_Source=ExcitationSource.INTERNAL, current_excitVal=1.00, custom_scale_name=""):
        """
        Creates channel(s) that use an IEPE velocity sensor to measure
        velocity.

        Args:
            physical_channel (str): Specifies the names of the physical
                channels to use to create virtual channels. The DAQ
                physical channel constant lists all physical channels on
                devices and modules installed in the system.
            name_to_assign_to_channel (Optional[str]): Specifies a name
                to assign to the virtual channel this function creates.
                If you do not specify a value for this input, ArtDAQ
                uses the physical channel name as the virtual channel
                name.
            min_val (Optional[float]): Specifies in **units** the
                minimum value you expect to measure.
            max_val (Optional[float]): Specifies in **units** the
                maximum value you expect to measure.
            units (Optional[artdaq.constants.ResistanceUnits]): Specifies the units to use to return resistance measurements.
            resistance_config (Optional[artdaq.constants.ResistanceConfiguration]): Specifies the resistance configuration for the channel.
                ArtDAQ uses this value for any resistance-based measurements,
                including temperature measurement using a thermistor or RTD.
            current_excit_Source (Optional[artdaq.constants.ExcitationSource]): Specifies the source of excitation.
            current_excitVal (Optional[float]):Specifies the amount of excitation that the sensor requires.
                If Voltage or Current is  ArtDAQ_Val_Voltage, this value is in volts.
                If Voltage or Current is  ArtDAQ_Val_Current, this value is in amperes.
            custom_scale_name (Optional[str]): Specifies the name of a
                custom scale for the channel. If you want the channel to
                use a custom scale, specify the name of the custom scale
                to this input and set **units** to
                **FROM_CUSTOM_SCALE**.
        Returns:
            artdaq._task_modules.channels.ai_channel.AIChannel:
            Indicates the newly created channel object.
        """
        cfunc = lib_importer.windll.ArtDAQ_CreateAIResistanceChan
        if cfunc.argtypes is None:
            with cfunc.arglock:
                if cfunc.argtypes is None:
                    cfunc.argtypes = [
                        lib_importer.task_handle, ctypes_byte_str,
                        ctypes_byte_str, ctypes.c_double, ctypes.c_double, ctypes.c_int,
                        ctypes.c_int, ctypes.c_int, ctypes.c_double, ctypes_byte_str]

        error_code = cfunc(
            self._handle, physical_channel, name_to_assign_to_channel,
            min_val, max_val, units.value,  resistance_config.value, current_excit_Source.value, current_excitVal, custom_scale_name)
        check_for_error(error_code)
        return self._create_chan(physical_channel, name_to_assign_to_channel)


    def add_ai_straingage_chan(
            self, physical_channel, name_to_assign_to_channel="",
            min_val=-0.001, max_val=0.001, units=StrainUnits.STRAIN,
            strain_config=StrainGageBridgeType.FULLBRIDGEI,
            voltage_excit_Source=ExcitationSource.INTERNAL, voltage_excitVal=2.50, gage_factor=2.0,
            initial_bridge_voltage=0.00, nominal_gage_resistance=350.00,  poisson_ratio=0.3,
            lead_wire_resistance=0.00, custom_scale_name=""):
        """
        Creates channel(s) that use an IEPE velocity sensor to measure
        velocity.

        Args:
            physical_channel (str): Specifies the names of the physical
                channels to use to create virtual channels. The DAQ
                physical channel constant lists all physical channels on
                devices and modules installed in the system.
            name_to_assign_to_channel (Optional[str]): Specifies a name
                to assign to the virtual channel this function creates.
                If you do not specify a value for this input, ArtDAQ
                uses the physical channel name as the virtual channel
                name.
            min_val (Optional[float]): Specifies in **units** the
                minimum value you expect to measure.
            max_val (Optional[float]): Specifies in **units** the
                maximum value you expect to measure.
            units (Optional[artdaq.constants.StrainUnits]): Specifies the units to use to return strain measurements from the channel.
            strain_config (Optional[artdaq.constants.StrainGageBridgeType]): Specifies the bridge configuration of the strain gages.
            voltage_excit_Source (Optional[artdaq.constants.ExcitationSource]): Specifies the source of excitation.
            voltage_excitVal (Optional[float]):Specifies the amount of excitation that the sensor requires.
                If Voltage or Current is  ArtDAQ_Val_Voltage, this value is in volts.
                If Voltage or Current is  ArtDAQ_Val_Current, this value is in amperes.
            gage_factor (Optional[float]):Specifies the sensitivity of the strain gage.  Gage factor relates the change
                in electrical resistance to the change in strain. Refer to the sensor documentation for this value.
            initial_bridge_voltage (Optional[float]):Specifies in volts the output voltage of the bridge while not under load.
                ArtDAQ subtracts this value from any measurements before applying scaling equations.  If you set Initial
                Bridge Ratio, ArtDAQ coerces this property to Initial Bridge Ratio times Actual Excitation Value.
                This property is set by ArtDAQ Perform Bridge Offset Nulling Calibration.
                If you set this property, ArtDAQ coerces Initial Bridge Ratio...
            nominal_gage_resistance (Optional[float]):Specifies in ohms the resistance of the bridge while not under load.
            poisson_ratio (Optional[float]):Specifies the ratio of lateral strain to axial strain in the material you are measuring.
            lead_wire_resistance (Optional[float]):The amount, in ohms, of resistance in the lead wires. Ideally,
                this value is the same for all leads.
            custom_scale_name (Optional[str]): Specifies the name of a
                custom scale for the channel. If you want the channel to
                use a custom scale, specify the name of the custom scale
                to this input and set **units** to
                **FROM_CUSTOM_SCALE**.
        Returns:
            artdaq._task_modules.channels.ai_channel.AIChannel:
            Indicates the newly created channel object.
        """
        cfunc = lib_importer.windll.ArtDAQ_CreateAIStrainGageChan
        if cfunc.argtypes is None:
            with cfunc.arglock:
                if cfunc.argtypes is None:
                    cfunc.argtypes = [
                        lib_importer.task_handle, ctypes_byte_str,
                        ctypes_byte_str, ctypes.c_double, ctypes.c_double, ctypes.c_int,
                        ctypes.c_int, ctypes.c_int, ctypes.c_double, ctypes.c_double, ctypes.c_double,
                        ctypes.c_double, ctypes.c_double, ctypes.c_double, ctypes_byte_str]

        error_code = cfunc(
            self._handle, physical_channel, name_to_assign_to_channel,
            min_val, max_val, units.value,  strain_config.value, voltage_excit_Source.value, voltage_excitVal, gage_factor,
            initial_bridge_voltage, nominal_gage_resistance, poisson_ratio, lead_wire_resistance, custom_scale_name)
        check_for_error(error_code)
        return self._create_chan(physical_channel, name_to_assign_to_channel)


    def add_ai_bridge_chan(
            self, physical_channel, name_to_assign_to_channel="",
            min_val=-0.1, max_val=0.1, units=BridgeUnits.VOLTSPERVOLT,
            bridge_config=BridgeConfiguration.HALFBRIDGE,
            voltage_excit_Source=ExcitationSource.INTERNAL, voltage_excitVal=2.5,
            nominal_bridge_resistance=0.001, custom_scale_name=""):
        """
        Creates channel(s) that use an IEPE velocity sensor to measure
        velocity.

        Args:
            physical_channel (str): Specifies the names of the physical
                channels to use to create virtual channels. The DAQ
                physical channel constant lists all physical channels on
                devices and modules installed in the system.
            name_to_assign_to_channel (Optional[str]): Specifies a name
                to assign to the virtual channel this function creates.
                If you do not specify a value for this input, ArtDAQ
                uses the physical channel name as the virtual channel
                name.
            min_val (Optional[float]): Specifies in **units** the
                minimum value you expect to measure.
            max_val (Optional[float]): Specifies in **units** the
                maximum value you expect to measure.
            units (Optional[artdaq.constants.BridgeUnits]): Specifies in which unit to return voltage ratios from the channel.
            bridge_config (Optional[artdaq.constants.BridgeConfiguration]): Specifies the bridge configuration of the strain gages.
            voltage_excit_Source (Optional[artdaq.constants.ExcitationSource]): Specifies the source of excitation.
            voltage_excitVal (Optional[float]):Specifies the amount of excitation that the sensor requires.
                If Voltage or Current is  ArtDAQ_Val_Voltage, this value is in volts.
                If Voltage or Current is  ArtDAQ_Val_Current, this value is in amperes.
            nominal_bridge_resistance (Optional[float]):Specifies in ohms the resistance of the bridge while not under load.
            custom_scale_name (Optional[str]): Specifies the name of a
                custom scale for the channel. If you want the channel to
                use a custom scale, specify the name of the custom scale
                to this input and set **units** to
                **FROM_CUSTOM_SCALE**.
        Returns:
            artdaq._task_modules.channels.ai_channel.AIChannel:
            Indicates the newly created channel object.
        """
        cfunc = lib_importer.windll.ArtDAQ_CreateAIBridgeChan
        if cfunc.argtypes is None:
            with cfunc.arglock:
                if cfunc.argtypes is None:
                    cfunc.argtypes = [
                        lib_importer.task_handle, ctypes_byte_str,
                        ctypes_byte_str, ctypes.c_double, ctypes.c_double, ctypes.c_int,
                        ctypes.c_int, ctypes.c_int, ctypes.c_double, ctypes.c_double,  ctypes_byte_str]

        error_code = cfunc(
            self._handle, physical_channel, name_to_assign_to_channel,
            min_val, max_val, units.value,  bridge_config.value, voltage_excit_Source.value, voltage_excitVal,
            nominal_bridge_resistance, custom_scale_name)
        check_for_error(error_code)
        return self._create_chan(physical_channel, name_to_assign_to_channel)

