"""
Daikin SkyZone platform that offers a climate device for Diakin Skyzone A/C.
"""
import logging
import time
from datetime import timedelta

import voluptuous as vol

import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.event import track_time_interval

from homeassistant.const import (
    CONF_HOST, CONF_ICON, CONF_MONITORED_CONDITIONS, CONF_NAME, CONF_SCAN_INTERVAL, CONF_PASSWORD
)
    
from homeassistant.helpers.discovery import load_platform

REQUIREMENTS = ['daikinPyZone==0.6']

_LOGGER = logging.getLogger(__name__)

DAIKIN_SKYZONE = 'skyzone_climate'
DOMAIN = 'skyzone'
SCAN_INTERVAL = timedelta(seconds=30)

CONF_DEFAULTNAME = 'Daikin Skyzone'
CONF_DEFAULTHOST = '0.0.0.0'
CONF_DEBUGLEVEL = 'debuglevel'
CONF_POLLEXTERNALSENS = 'pollextsensors'
CONF_DEFAULTPASSWORD = '0000'
DEFAULT_DEBUGLEVEL = 0
RETRY_LIMIT = 5

COMPONENT_TYPES = ['climate', 'sensor','switch']

CONF_SENSOR_ICON = 'mdi:thermometer'
CONF_ZONESWITCH_ICON = 'mdi:radiobox-marked'
CONF_TEMPSWITCH_ICON = 'mdi:layers'


CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema({
        vol.Optional(CONF_HOST, default=CONF_DEFAULTHOST): cv.string,
        vol.Optional(CONF_NAME, default=CONF_DEFAULTNAME): cv.string,
        vol.Optional(CONF_PASSWORD, default=CONF_DEFAULTPASSWORD): cv.string,
        vol.Optional(CONF_SCAN_INTERVAL, default=SCAN_INTERVAL): cv.time_period,
        vol.Optional(CONF_DEBUGLEVEL, default=DEFAULT_DEBUGLEVEL): cv.positive_int,
        vol.Optional(CONF_POLLEXTERNALSENS, default=DEFAULT_DEBUGLEVEL): cv.positive_int
    })
}, extra=vol.ALLOW_EXTRA)


def setup(hass,  config):
    """Establish connection with Skyzone."""
    name = config[DOMAIN][CONF_NAME]
    scanInterval = config[DOMAIN][CONF_SCAN_INTERVAL]
    ipAddress = config[DOMAIN][CONF_HOST]
    debugLvl = config[DOMAIN][CONF_DEBUGLEVEL]
    pollExtSns = config[DOMAIN][CONF_POLLEXTERNALSENS]
    password = config[DOMAIN][CONF_PASSWORD]
        
    skyzoneAPI = skyZone_setup(hass, password, name, ipAddress, debugLvl, pollExtSns)
    
    if skyzoneAPI is None:
        return False
        
    discovery_info = {}

    #Trigger load of Climate, Sensor and Switch components
    for component in COMPONENT_TYPES:
        load_platform(hass, component, DOMAIN, discovery_info, config)
 
    #handle update triggers
    def BasicUpdate(event_time):
        hass.data[DAIKIN_SKYZONE].BasicUpdate()
        
    def TempSensorSkyzone(event_time):
        hass.data[DAIKIN_SKYZONE].TempSensorUpdate()
        
    def ExternalTempSensorSkyzone(event_time):
        if(pollExtSns == 1):
            hass.data[DAIKIN_SKYZONE].ExternalTempSensorUpdate()
            
    #Skyzone controller sometimes drops connected IP, so requires a resync once in a while. STock unit does 5min. 1 hour should be ok.
    def ReSyncSkyzone(event_time):
        hass.data[DAIKIN_SKYZONE].discover_skyzoneController()
        
    # Call the API to refresh updates
    # Split into seperate processes to attempt to keep update time under 10s.
    track_time_interval(hass,BasicUpdate, scanInterval)
    track_time_interval(hass,TempSensorSkyzone, scanInterval)
    track_time_interval(hass,ExternalTempSensorSkyzone, (scanInterval*3))
    #Skyzone controller sometimes drops connected IP, so requires a resync once in a while. STock unit does 5min. 1 hour should be ok.
    track_time_interval(hass,ReSyncSkyzone, timedelta(seconds=3600))
    
    return True


def skyZone_setup(hass,password, name, ipAddress, debugLvl, pollExtSns):
    from daikinPyZone import DaikinSkyZone
    daikinSkyzone = hass.data[DAIKIN_SKYZONE] =  DaikinSkyZone(password, name, ipAddress, debugLvl, pollExtSns)

    retryCount = 0   
    while(retryCount < RETRY_LIMIT):
        if (daikinSkyzone.discover_skyzoneController() == 0):
            _LOGGER.info("Retrying discovery of SkyZone unit.")
            retryCount +=1
        else:
            break 

    if(daikinSkyzone.IsUnitConnected()):       
        return daikinSkyzone
    else:
        return None
