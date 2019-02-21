"""
Support for Daikin Skyzone Sensors.
For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/xxxxxxxxxxxxxxx/
"""
import logging
import voluptuous as vol

import homeassistant.helpers.config_validation as cv

from homeassistant.components.switch import SwitchDevice

from . import (DAIKIN_SKYZONE, CONF_ZONESWITCH_ICON, CONF_TEMPSWITCH_ICON)

def setup_platform(hass, config, add_devices, discovery_info=None):
   #pull skyzone from base component
    daikinSkyZone = hass.data[DAIKIN_SKYZONE]
    switches = []
    
    if(daikinSkyZone.IsUnitConnected()):              
        #loop over supported zones
        for x in range (daikinSkyZone.GetNumberOfZones()):
            switches.append(DaikinClimateZoneSwtich(daikinSkyZone, x ))
            
        #If no external sensors are present, no need to add temp sensor selection options
        if(daikinSkyZone.GetNumberExternalSensors() > 0):
            switches.append(DaikinClimateTempSwtich(daikinSkyZone, 0 )) #Internal
            for x in range (daikinSkyZone.GetNumberExternalSensors()):
                switches.append(DaikinClimateTempSwtich(daikinSkyZone, (x+1) )) #External 1/2

        add_devices(switches, True)

        return True
    else:
        return False
        

class DaikinClimateZoneSwtich(SwitchDevice):
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
        return self._PiZone.GetZoneName(self._zoneIndex)
        
    @property
    def is_on(self):
        """Call GetSensorState function."""
        return self._PiZone.GetZonesState(self._zoneIndex)
            
    @property
    def available(self):
        """Always return true."""
        return True

    def turn_on(self, **kwargs):
        """Turn the zone on."""
        self._PiZone.SetZoneActive(self._zoneIndex)
        self._PiZone.SyncClimateSettingsData()

    def turn_off(self, **kwargs):
        """Turn the zone off."""
        self._PiZone.SetZoneInactive(self._zoneIndex)
        self._PiZone.SyncClimateSettingsData()
        
class DaikinClimateTempSwtich(SwitchDevice):
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
        return self._PiZone.GetSensorName(self._sensorIndex)
        
    @property
    def is_on(self):
        """Call GetSensorState function."""
        return self._PiZone.GetSensorState(self._sensorIndex)
            
    @property
    def available(self):
        """Always return true."""
        return True

    def turn_on(self, **kwargs):
        """Turn the switch on, select the current sensor index."""
        self._PiZone.SetSelectedTempSensor(self._sensorIndex)
        self._PiZone.SyncClimateSensor()
        
    def turn_off(self, **kwargs):
        """Not allowed to turn on. Turning on another sensor will turn on the other."""
        False
        