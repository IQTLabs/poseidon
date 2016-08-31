#!/usr/bin/env python
#
#   Copyright (c) 2016 In-Q-Tel, Inc, All Rights Reserved.
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
"""
Created on 15 July 2016
@author: dgrossman
"""
import logging
import os
import urllib2

from poseidon.baseClasses.Main_Action_Base import Main_Action_Base
DOCKER_URL = 'file:///poseidonWork/templates/config.template'
CI_TESTING = '/poseidonWork/templates/config.template'


module_logger = logging.getLogger(__name__)


class Config(Main_Action_Base):

    def __init__(self):
        super(Config, self).__init__()
        self.mod_name = self.__class__.__name__
        self.URL = None
        if self.logger is None:
            self.logger = module_logger
        try:
            self.URL = os.environ['POSEIDON_CONFIG_URL']
        except KeyError:
            # TODO flag error
            self.URL = CI_TESTING
            logLine = 'poseidonMain:Config using {0}'.format(self.URL)
            self.logger.debug(logLine)

    def get_section(self, section_name):
        if self.URL == CI_TESTING:
            import ConfigParser
            config = ConfigParser.ConfigParser()
            config.readfp(open(self.URL), 'r')
            return config.items(section_name)
        if self.URL is not None:
            if self.URL[-1] != '/':
                ask = self.URL + '/' + section_name
            else:
                ask = self.URL + section_name
            retval = urllib2.urlopen(ask).readlines()
            logLine = 'ask={0}\n retval={1}\n'.format(ask, retval)
            self.logger.debug(logLine)
            return retval
        # TODO flag error?
        return None


config_interface = Config()
