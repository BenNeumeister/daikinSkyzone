"""
Support for Daikin Skyzone Climate.
For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/xxxxxxxxxxxxxxx/
"""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.const import UnitOfTemperature, ATTR_TEMPERATURE
from homeassistant.components.climate import (
    ATTR_PRESET_MODE,
    PRESET_ACTIVITY,
    PRESET_AWAY,
    PRESET_COMFORT,
    PRESET_ECO,
    PRESET_HOME,
    PRESET_NONE,
    PRESET_SLEEP,
    ClimateEntity,
    ClimateEntityFeature,
    HVACAction,
    HVACMode,
)

from . import DAIKIN_SKYZONE

ATTR_NUM_OF_ZONES = 'number_of_zones'
ATTR_NUM_OF_EXT_SENSORS = 'number_of_external_sensors'
ATTR_ERROR_CODES = 'error_codes'
ATTR_HISTORY_ERROR_CODES = 'history_error_codes'
ATTR_CLEAR_FILTER = 'clear_filter_warning'
ATTR_INDOOR_UNIT = 'indoor_unit'
ATTR_OUTDOOR_UNIT = 'outdoor_unit'

SUPPORT_FLAGS = (ClimateEntityFeature.TURN_ON
	| ClimateEntityFeature.TURN_OFF
	| ClimateEntityFeature.TARGET_TEMPERATURE
	| ClimateEntityFeature.FAN_MODE)
        
def setup_platform(hass, config, add_devices, discovery_info=None):
    """Set up the SkyZone climate devices."""
    #pull skyzone from base component
    daikinSkyzone = hass.data[DAIKIN_SKYZONE]

    if(daikinSkyzone.is_unit_connected()):       
        #once initial data received, add device.
        add_devices([  DaikinSkyZoneClimate(daikinSkyzone)    ])

        return True
    else:
        return False
        

class DaikinSkyZoneClimate(ClimateEntity):
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
        return UnitOfTemperature.CELSIUS

    @property
    def target_temperature(self):
        """Return the temperature we try to reach."""
        return self._PiZone.get_target_temp()

    @property
    def current_temperature(self):
        """Return the current temperature."""
        return self._PiZone.get_current_temp()
        
    @property
    def target_temperature_step(self):
        """Return the supported step of target temperature."""
        return 1

    @property
    def hvac_mode(self):
        """Return current operation ie. heat, cool, idle."""
        return OPERATION_MODES[self._PiZone.get_current_mode()]

    @property
    def hvac_modes(self):
        """Return the list of available operation modes."""
        from daikinPyZone.daikinClasses import (OPERATION_MODES_MAP)
        return sorted(OPERATION_MODES_MAP.keys(), key=OPERATION_MODES_MAP.get)

    @property
    def hvac_action(self):
        """Return the current running hvac operation if supported.
        Need to be one of HVACAction*.
        """
        if OPERATION_MODES[self._PiZone.get_current_mode()] == HVACMode.OFF:
            return HVACAction.OFF
        if OPERATION_MODES[self._PiZone.get_current_mode()] == HVACMode.COOL:
            return HVACAction.COOLING
        if OPERATION_MODES[self._PiZone.get_current_mode()] == HVACMode.HEAT:
            return HVACAction.HEATING
        if OPERATION_MODES[self._PiZone.get_current_mode()] == HVACMode.DRY:
            return HVACAction.DRYING
        if OPERATION_MODES[self._PiZone.get_current_mode()] == HVACMode.FAN_ONLY:
            return HVACAction.FAN
        return HVACAction.IDLE

    @property
    def fan_mode(self):
        """Return the fan setting."""
        return FAN_MODES[self._PiZone.get_fan_speed()]

    @property
    def fan_modes(self):
        """Return the list of available fan modes."""
        from daikinPyZone.daikinClasses import (FAN_MODE_MAP)
        return sorted(FAN_MODE_MAP.keys(), key=FAN_MODE_MAP.get)
     
    def set_temperature(self, **kwargs):
        """Set new target temperature."""
        if kwargs.get(ATTR_TEMPERATURE) is not None:
            self._PiZone.set_target_temp(kwargs.get(ATTR_TEMPERATURE))
            self._PiZone.sync_climate_request()

    def set_hvac_mode(self, operation_mode):
        """Set new operation mode."""
        self._PiZone.set_current_mode(OPERATION_MODES_MAP[operation_mode])
        self._PiZone.sync_climate_request()

    def set_fan_mode(self, fan_mode):
        """Set new fan mode."""
        self._PiZone.set_fan_speed(FAN_MODE_MAP[fan_mode])
        self._PiZone.sync_climate_request()
        
    @property
    def min_temp(self):
        """Return the minimum temperature."""
        return self._PiZone.get_min_supported_temp()

    @property
    def max_temp(self):
        """Return the maximum temperature."""
        return self._PiZone.get_max_supported_temp()
        
    @property
    def extra_state_attributes(self):
        """Return the optional device state attributes."""
        return {
            ATTR_INDOOR_UNIT: self._PiZone.get_indoor_unit_part_number(),
            ATTR_OUTDOOR_UNIT: self._PiZone.get_outdoor_unit_part_number(),
            ATTR_NUM_OF_ZONES: self._PiZone.get_number_of_zones(),
            ATTR_NUM_OF_EXT_SENSORS: self._PiZone.get_number_of_external_sensors(),
            ATTR_ERROR_CODES: self._PiZone.get_error_codes(),
            ATTR_HISTORY_ERROR_CODES: self._PiZone.get_history_error_codes(),
            ATTR_CLEAR_FILTER: self._PiZone.get_clear_filter_flag()
        }
