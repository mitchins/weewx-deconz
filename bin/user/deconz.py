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
# [Deconz]
#  This section is for the Deconz data service.
    
#  The url to use
#  sensorURL = http://192.168.3.131:8888/api/30C70FAF3A/sensors/19

# Tell weewx about the service by adding it to weewx.conf:

# [Engine]
#     [[Services]]
#         data_services = ..., _

#  [[sensor_map]]
#     pressure = pressure

import syslog
import weewx
from weewx.wxengine import StdService
import urllib.request
import json

class DeconzService(StdService):
    def __init__(self, engine, config_dict):
        super(DeconzService, self).__init__(engine, config_dict)    
        d = config_dict.get('DeconzService', {})
        self.sensor_url = d.get('sensorURL', '')
        syslog.syslog(syslog.LOG_INFO, "deconz: using %s" % self.sensor_url)
        self._sensor_map = d.get('sensor_map', {})
        self.bind(weewx.NEW_ARCHIVE_RECORD, self.read_url)

    def read_url(self, event):
        try:
          with urllib.request.urlopen(self.sensor_url) as f:
            data = json.loads(r.decode('utf-8'))
            syslog.syslog(syslog.LOG_DEBUG, "deconz: received %s" % data)
            state = data['state']
            for target, alias in self._sensor_map.items():
              if alias in state:
                event.record[target] = float(state[alias])
        except Exception as e:
            syslog.syslog(syslog.LOG_ERR, "deconz: cannot read url: %s" % e)