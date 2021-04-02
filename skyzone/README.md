# Daikin Skyzone Home Assintant - Custom Component
Supported Skyzone controllers: BRC230TZ4, BRC230TZ8, BRC24TZ4 and BRC24TZ8
Supported Daikin Models: Any FDYQ & FDYQN unit fitted with a Skyzone controller (Single or 3 phase)

Drop it into your custom_components folder and just simply add the ‘skyzone:’ tag into your config and done.
Full discovery supported. It will add in the climate module, temperature sensors and zones.

## Supported Features

 - Set/Get heating/cooling temperature
 - Set/Get AC mode (heat/cool/fan/dry/off)
 - Set/Get AC FAN setting (Auto/Low/Med/Hi/Auto-Low/Auto-Med/Auto-High)
 - Get current temperatures from internal, outdoor and refrigerant sensors.
 - Support for external sensors connected to Daikin Unit including names. (Current temp for external sensors will only be shown if an external sensor is set as the 'selected sensor').
 - Set/View current zones (As setup by the Daikin Tablet).
 - Set/View current selected sensor (Reference temperature used by Daikin to start/stop climate control)
 - View setup info from Daikin AC (Number of Zones/Sensors, Internal/External Part Numbers, Current and History Error codes and clean filter warning flag).

## configuration.yaml

99% of users all you will need is;

	skyzone:

The other 1%;

	skyzone:
	  name: 'Daikin Climate Control' (optional) 
	  password: 1234 (optional) 
	  host: 192.168.1.101 (optional) 
	  scan_interval: 60 (optional) 
	  debuglevel: 2 (optional) 
	  pollextsensors: 0 (optional) 
  
|Parameter | Purpose/Options
|-------|--------|
|name|Give the Climate instance a specific name for HA/Google Home/Alexa. Default is ‘Daikin Skyzone’
|password|Adapter password as configured in the Daikin Tablet. API will show an error if this is wrong or needed.
|host|Set the Daikin AP IP address if you want to bypass discovery. Might save 2-3 seconds during init
|scan_interval|Set how often the API is polled. 60 seconds is default.<br>I wouldn’t go any lower than 30seconds as you risk much overlapping.<br>Any higher and you risk loosing refrigerant temp data, especially when it goes into de-ice or a lubrication cycle.
|debuglevel|0 - Disabled (default)<br>1 - See information updated as it comes in and polling flags<br>2 - See raw info received from unit. Only really useful if somethings not working right.<br>For debugging, you will need to configure the logging component and monitor for ‘debug’.
|pollextsensor|0 - Disabled (default)<br>1 - Enabled. Will trigger the API to switch between external sensors every 3minutes instead of showing ‘Unknown’.<br>Has some side-affects as the Daikin unit itself will use this value for ~3mins.<br>So if your zones have very different temperatures, don’t use it.
