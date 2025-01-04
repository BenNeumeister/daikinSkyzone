"""
Support for Daikin Skyzone Sensors.
For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/xxxxxxxxxxxxxxx/
"""
import logging
import voluptuous as vol

import homeassistant.helpers.config_validation as cv

from homeassistant.components.switch import SwitchEntity

from . import (DAIKIN_SKYZONE, CONF_ZONESWITCH_ICON, CONF_TEMPSWITCH_ICON)

def setup_platform(hass, config, add_devices, discovery_info=None):
   #pull skyzone from base component
    daikinSkyZone = hass.data[DAIKIN_SKYZONE]
    switches = []
    
    if(daikinSkyZone.is_unit_connected()):              
        #loop over supported zones
        for x in range (daikinSkyZone.get_number_of_zones()):
            switches.append(DaikinClimateZoneSwtich(daikinSkyZone, x ))
            
        #If no external sensors are present, no need to add temp sensor selection options
        if(daikinSkyZone.get_number_of_external_sensors() > 0):
            switches.append(DaikinClimateTempSwtich(daikinSkyZone, 0 )) #Internal
            for x in range (daikinSkyZone.get_number_of_external_sensors()):
                switches.append(DaikinClimateTempSwtich(daikinSkyZone, (x+1) )) #External 1/2

        add_devices(switches, True)

        return True
    else:
        return False
        

class DaikinClimateZoneSwtich(SwitchEntity):
    """Representation of a Switch - Zone."""

    def __init__(self, PiZone, zoneIndex):
        """Initialize the sensor."""
        self._PiZone = PiZone
        self._zoneIndex= zoneIndex
        self._icon = CONF_ZONESWITCH_ICON 

    @property
    def icon(self):
        """Icon to use in the frontend."""
        return self._icon

    @property
    def name(self):
        """Return the name of the zone."""
        return self._PiZone.get_zone_name(self._zoneIndex)
        
    @property
    def is_on(self):
        """Call GetSensorState function."""
        return self._PiZone.get_zone_state(self._zoneIndex)
            
    @property
    def available(self):
        """Always return true."""
        return True

    def turn_on(self, **kwargs):
        """Turn the zone on."""
        self._PiZone.set_zone_active(self._zoneIndex)
        self._PiZone.sync_climate_request()

    def turn_off(self, **kwargs):
        """Turn the zone off."""
        self._PiZone.set_zone_inactive(self._zoneIndex)
        self._PiZone.sync_climate_request()
        
class DaikinClimateTempSwtich(SwitchEntity):
    """Representation of a Switch for the Sensor select."""

    def __init__(self, PiZone, sensorIndex):
        """Initialize the sensor."""
        self._PiZone = PiZone
        self._sensorIndex= sensorIndex
        self._icon = CONF_TEMPSWITCH_ICON 

    @property
    def icon(self):
        """Icon to use in the frontend."""
        return self._icon

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._PiZone.get_sensor_name(self._sensorIndex)
        
    @property
    def is_on(self):
        """Call GetSensorState function."""
        return self._PiZone.get_sensor_state(self._sensorIndex)
            
    @property
    def available(self):
        """Always return true."""
        return True

    def turn_on(self, **kwargs):
        """Turn the switch on, select the current sensor index."""
        self._PiZone.set_selected_temp_sensor(self._sensorIndex)
        self._PiZone.update_temperate_sensor()
        
    def turn_off(self, **kwargs):
        """Not allowed to turn on. Turning on another sensor will turn on the other."""
        False
        
