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
Created on 17 August 2016
@author: aganeshLab41, tlanham

Test module for machine learning algorithm
for classifying device type from tcp packets.
"""
import pytest
from dev_classifier import rabbit_init


@pytest.mark.skip(reason='requires rabbitmq broker, integration test')
def test_rabbit_init():
    channel, connection = rabbit_init(host='poseidon-rabbit',
                                      exchange='topic-poseidon-internal',
                                      queue_name='features_flowparser')
