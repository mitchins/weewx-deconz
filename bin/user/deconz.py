#!/usr/bin/python
#
# weewx driver that reads data from deconz REST API
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.
#
# See http://www.gnu.org/licenses/

#
# The units must be weewx.US:
#   degree_F, inHg, inch, inch_per_hour, mile_per_hour
#
# To use this driver, put this file in the weewx user directory, then make
# the following changes to weewx.conf:
#
# [DeconzService]
#  This section is for the Deconz data service.
    
#  The url to use
#  sensorURL = http://192.168.3.131:8888/api/30C70FAF3A/sensors/19
#  [[sensor_map]]
#     pressure = pressure

# Tell weewx about the service by adding it to weewx.conf:

# [Engine]
#     [[Services]]
#         data_services = ..., _



import syslog
import weewx
from weewx.wxengine import StdService
import urllib.request
import json

# New-style weewx logging
import weeutil.logger
import logging
log = logging.getLogger(__name__)

def logdbg(msg):
  log.debug(msg)

def loginf(msg):
  log.info(msg)

def logerr(msg):
  log.error(msg)

class DeconzService(StdService):
    def __init__(self, engine, config_dict):
        super(DeconzService, self).__init__(engine, config_dict)    
        d = config_dict.get('Deconz', {})
        self.sensor_url = d.get('sensorURL', '')
        loginf("deconz: using %s" % self.sensor_url)
        self._sensor_map = d.get('sensor_map', {})
        self.bind(weewx.NEW_ARCHIVE_RECORD, self.read_url)

    def read_url(self, event):
        try:
          with urllib.request.urlopen(self.sensor_url) as r:
            data = json.loads(r.read().decode('utf-8'))
            logdbg("deconz: received %s" % data)
            state = data['state']
            for target, alias in self._sensor_map.items():
              if alias in state:
                value = float(state[alias])
                # todo: neat etc. manage many-many mappings names/units
                if alias == 'pressure':
                  # convert hPa to inHG  
                  event.record[target] = value * 0.029529983071445
        except Exception as e:
            logerr("deconz: cannot read url: %s" % e)