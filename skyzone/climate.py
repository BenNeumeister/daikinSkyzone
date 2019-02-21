"""
Support for Daikin Skyzone Climate.
For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/xxxxxxxxxxxxxxx/
"""
import logging
import voluptuous as vol

import homeassistant.helpers.config_validation as cv

from homeassistant.const import (
    CONF_NAME, TEMP_CELSIUS, ATTR_TEMPERATURE
)

from homeassistant.components.climate import (
    PLATFORM_SCHEMA, SUPPORT_FAN_MODE, SUPPORT_OPERATION_MODE, SUPPORT_TARGET_TEMPERATURE,
    ClimateDevice)    

from . import DAIKIN_SKYZONE

ATTR_NUM_OF_ZONES = 'number_of_zones'
ATTR_NUM_OF_EXT_SENSORS = 'number_of_external_sensors'
ATTR_ERROR_CODES = 'error_codes'
ATTR_HISTORY_ERROR_CODES = 'history_error_codes'
ATTR_CLEAR_FILTER = 'clear_filter_warning'
ATTR_INDOOR_UNIT = 'indoor_unit'
ATTR_OUTDOOR_UNIT = 'outdoor_unit'

SUPPORT_FLAGS = (SUPPORT_TARGET_TEMPERATURE  | SUPPORT_OPERATION_MODE | SUPPORT_FAN_MODE )

def setup_platform(hass, config, add_devices, discovery_info=None):
    """Set up the SkyZone climate devices."""
    #pull skyzone from base component
    daikinSkyzone = hass.data[DAIKIN_SKYZONE]

    if(daikinSkyzone.IsUnitConnected()):       
        #once initial data received, add device.
        add_devices([  DaikinSkyZoneClimate(daikinSkyzone)    ])

        return True
    else:
        return False
        

class DaikinSkyZoneClimate(ClimateDevice):
    def __init__(self, PiZone):
        self._PiZone = PiZone

    @property
    def supported_features(self):
        """Return the list of supported features."""
        return SUPPORT_FLAGS

    @property
    def name(self):
        """Return the name of the climate device."""
        return self._PiZone._name
        
    @property
    def temperature_unit(self):
        """Return the unit of measurement."""
        return TEMP_CELSIUS

    @property
    def target_temperature(self):
        """Return the temperature we try to reach."""
        return self._PiZone.GetTargetTemp()

    @property
    def current_temperature(self):
        """Return the current temperature."""
        return self._PiZone.GetCurrentTempValue()
        
    @property
    def target_temperature_step(self):
        """Return the supported step of target temperature."""
        return 1

    @property
    def current_operation(self):
        """Return current operation ie. heat, cool, idle."""
        from daikinPyZone.daikinClasses import (OPERATION_MODES)
        return OPERATION_MODES[self._PiZone.GetCurrentMode()]

    @property
    def operation_list(self):
        """Return the list of available operation modes."""
        from daikinPyZone.daikinClasses import (OPERATION_MODES_MAP)
        return sorted(OPERATION_MODES_MAP.keys(), key=OPERATION_MODES_MAP.get)

    @property
    def current_fan_mode(self):
        """Return the fan setting."""
        from daikinPyZone.daikinClasses import (FAN_MODES)
        return FAN_MODES[self._PiZone.GetFanSpeed()]

    @property
    def fan_list(self):
        """Return the list of available fan modes."""
        from daikinPyZone.daikinClasses import (FAN_MODE_MAP)
        return sorted(FAN_MODE_MAP.keys(), key=FAN_MODE_MAP.get)
     
    def set_temperature(self, **kwargs):
        """Set new target temperature."""
        if kwargs.get(ATTR_TEMPERATURE) is not None:
            self._PiZone.SetTargetTemp(kwargs.get(ATTR_TEMPERATURE))
        self._PiZone.SyncClimateSettingsData()

    def set_operation_mode(self, operation_mode):
        """Set new operation mode."""
        from daikinPyZone.daikinClasses import (OPERATION_MODES_MAP)
        self._PiZone.SetCurrentMode(OPERATION_MODES_MAP[operation_mode])
        self._PiZone.SyncClimateSettingsData()

    def set_fan_mode(self, fan_mode):
        """Set new fan mode."""
        from daikinPyZone.daikinClasses import (FAN_MODE_MAP)
        self._PiZone.SetFanSpeed(FAN_MODE_MAP[fan_mode])
        self._PiZone.SyncClimateSettingsData()
        
    @property
    def min_temp(self):
        """Return the minimum temperature."""
        return self._PiZone.GetMinSupportTemp()

    @property
    def max_temp(self):
        """Return the maximum temperature."""
        return self._PiZone.GetMaxSupportTemp()
        
    @property
    def device_state_attributes(self):
        """Return the optional device state attributes."""
        return {
            ATTR_INDOOR_UNIT: self._PiZone.GetIndoorUnitPartNumber(),
            ATTR_OUTDOOR_UNIT: self._PiZone.GetOutdoorUnitPartNumber(),
            ATTR_NUM_OF_ZONES: self._PiZone.GetNumberOfZones(),
            ATTR_NUM_OF_EXT_SENSORS: self._PiZone.GetNumberExternalSensors(),
            ATTR_ERROR_CODES: self._PiZone.GetErrorCodes(),
            ATTR_HISTORY_ERROR_CODES: self._PiZone.GetHistoryErrorCodes(),
            ATTR_CLEAR_FILTER: self._PiZone.GetClearFilterFlag()
        }