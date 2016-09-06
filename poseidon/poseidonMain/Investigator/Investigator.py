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
'''
Module for applying user-defined rules to
network flows.

Created on 17 May 2016
@author: dgrossman, tlanham
'''
import ast
import logging
import logging.config
import sys
import urllib
import requests
import json

from poseidon.baseClasses.Main_Action_Base import Main_Action_Base
from poseidon.poseidonMain.Config.Config import Config


module_logger = logging.getLogger(__name__)


class Investigator(Main_Action_Base):

    def __init__(self):
        super(Investigator, self).__init__()
        self.logger = module_logger
        self.mod_name = self.__class__.__name__
        self.config = Config()
        self.config_dict = {}
        self.update_config()
        self.handles = dict()

        self.algos = {}
        self.rules = {}
        self.update_rules()

        self.vent_machines = {}
        self.vctrl_list()
        self.vctrl_startup()
        self.vctrl_addr = 'http://' + self.config_dict['vctrl_addr']

    def vctrl_list(self):
        '''
        Retrieves list of vent machines running on vcontrol
        instance. Gets list of machines as json and evaluates
        into dict to update dict of available vent machines.
        '''
        try:
            resp = requests.get(self.vctrl_addr + '/machines/list')
            self.vent_machines = ast.literal_eval(resp.body)
        except:
            self.logger.error('Main: Investigator: error on vctrl list')

    def vctrl_startup(self):
        '''
        For each vent endpoint machine descriped in the Investigator
        config section, registers the machine with vcontrol.
        '''
        for machine, config in self.vent_machines.iteritems():
            try:
                resp = requests.post(
                    self.vctrl_addr + '/machines/create', data={'machine':'vent1'})
            except:
                self.logger.error(
                    'Main: Investigator: error on vent create request.')

    @staticmethod
    def format_vent_create(name, provider, body=None, group='poseidon-vent', labels='default', memory=4096, cpus=4, disk_sz=20000):
        '''
        Formats body dict for vcontrol machine create.
        Returns dict for vcontrol create request.

        NOTE: name and provider are required parameters,
        the rest can be covered by defaults.
        '''
        body = body or {}
        body['name'] = name
        body['provider'] = provider
        if 'group' not in body:
            body['group'] = group
        if 'labels' not in body:
            body['labels'] = labels
        if 'memory' not in body:
            body['memory'] = memory
        if 'cpus' not in body:
            body['cpus'] = cpus
        if 'disk_sz' not in body:
            body['disk_sz'] = disk_sz
        return body

    def update_config(self):
        '''
        Updates configuration based on config file
        (for changing rules).
        '''
        self.config_dict = dict(self.config.get_section('Investigator'))

    def update_rules(self):
        '''
        Updates rules dict from config,
        removes algorithms that are not
        registered.
        '''
        self.update_config()
        for key in self.config_dict:
            if 'policy' in key:
                self.rules[key] = self.config_dict[key].split(' ')

        for policy in self.rules:
            for proposed_algo in self.rules[policy]:
                if proposed_algo not in self.algos:
                    ostr = 'algorithm: {0} has not been registered, deleting from policy'.format(
                        proposed_algo)
                    self.logger.error(ostr)
                    del proposed_algo

    def register_algorithm(self, name, algorithm):
        '''
        Register investigation algorithm.

        NOTE: for production, replace registering function
        pointers with info about the algorithm (path,
        complexity, etc).
        '''
        if name not in self.algos:
            self.algos[name] = algorithm
            return True
        return False

    def delete_algorithm(self, name):
        if name in self.algos:
            self.algos.pop(name)
            return True
        return False

    def count_algorithms(self):
        return len(self.algos)

    def get_algorithms(self):
        return self.algos

    def clear(self):
        self.algos.clear()

    def process_new_machine(self, ip_addr):
        '''
        Given the ip of a machine added to the network,
        requests information from the database about the
        ip, then processes accordingly.
        '''
        query = {'node_ip': ip_addr}
        uri = 'http://poseidon-storage-interface/v1/poseidon_records/network_graph/' + json.dumps(query)
        try:
            resp = requests.get(uri)
        except:
            # error connecting to storage interface
            # log error
            self.logger.error(
                'Main (Investigator): could not connect to storage interface')
            return

        resp = ast.literal_eval(resp.body)
        if resp['count'] <= 0:
            # machine has no info in db or error on query
            pass
        elif resp['count'] == 1:
            # there is a record for machine
            info = resp['body']
        else:
            # bad - should only be one record for each ip
            # log error for investigation
            ostr = 'duplicate record for machine: {0}'.format(ip_addr)
            self.logger.error(ostr)

    def get_handlers(self, t):
        handle_list = []
        if t in self.handles:
            handle_list.append(self.handles[t])

        for helper in self.actions.itervalues():
            if t in helper.handles:
                handle_list.append(helper.handles[t])
        return handle_list


class Investigator_Response(Investigator):
    '''
    Investigator_Response manages and tracks the
    system response to an event (ie new machine
    added to network, etc). Maintains a record of
    jobs scheduled
    '''

    def __init__(self):
        super(Investigator_Response, self).__init__()
        self.logger = module_logger
        self.jobs = {}

    def vent_preparation(self):
        '''
        Prepares vent jobs based on algorithms
        available to be used and investigator
        rules.
        '''
        for machine in self.vent_machines:
            try:
                url = 'http://' + self.vctrl_addr + '/commands/deploy/' + machine
                resp = requests.post(url)
            except:
                self.logger.error(
                    'Main: Investigator: vent_preparation, vent request failed')

    def send_vent_jobs(self):
        '''
        Connects to vent and sends prepared
        jobs for analysis, waits for results
        and then continues with appropriate
        response.
        '''
        try:
            resp = requests.get('vent_url')
        except:
            self.logger.error(
                'Main: Investigator: send_vent_jobs, vent request failed')

    @staticmethod
    def update_record():
        '''
        Update database based on processing
        results and update network posture.
        '''
        try:
            url = 'http://poseidon-storage-interface/v1/'
            resp = requests.get(url)
        except:
            pass


investigator_interface = Investigator()
