"""
Support for Daikin Skyzone Sensors.
For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/xxxxxxxxxxxxxxx/
"""
import logging
import voluptuous as vol

import homeassistant.helpers.config_validation as cv

from homeassistant.helpers.entity import Entity
from homeassistant.util.unit_system import UnitSystem

from custom_components.skyzone import (
    DAIKIN_SKYZONE, CONF_SENSOR_ICON)

def setup_platform(hass, config, add_devices, discovery_info=None):
   #pull skyzone from base component
    daikinSkyzone = hass.data[DAIKIN_SKYZONE]
    units = hass.config.units
    sensors = []
    
    if(daikinSkyzone.IsUnitConnected()):              
        #loop over enabled sensors
        #1,2 and 3 are default enabled sensors (Internal, Outdoor and Coolant)
        #External  sensors can be from 0 to 2 depending on hardware connected to AC.

        for x in range (3 + daikinSkyzone.GetNumberExternalSensors()):
            sensors.append(DaikinClimateSensor(daikinSkyzone, x , units))

        add_devices(sensors, True)

        return True
    else:
        return False
        

class DaikinClimateSensor(Entity):
    """Representation of a Sensor."""

    def __init__(self, PiZone, sensorIndex, units: UnitSystem):
        """Initialize the sensor."""
        self._PiZone = PiZone
        self._sensorIndex= sensorIndex
        self._icon = CONF_SENSOR_ICON 
        self._unit_of_measurement = units.temperature_unit

    @property
    def icon(self):
        """Icon to use in the frontend,."""
        return self._icon

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._PiZone.GetSensorName(self._sensorIndex)

    @property
    def state(self):
        """Return the value of the sensor."""
        return self._PiZone.GetSensorValue(self._sensorIndex)

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return self._unit_of_measurement