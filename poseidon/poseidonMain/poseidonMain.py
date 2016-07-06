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
poseidonMain

Created on 29 May 2016
@author: dgrossman, lanhamt
"""
import json
from os import environ
from subprocess import call
from subprocess import check_output

from PoseidonPlanner.PoseidonPlanner import PoseidonPlanner
from PoseidonSurvey.PoseidonSurvey import PoseidonSurvey


class PoseidonMain:

    def __init__(self):
        self.modName = 'PoseidonMain'

    def goTime(self):
        return True


def main():
    pMain = PoseidonMain()
    pPlanner = PoseidonPlanner()
    pSurvey = PoseidonSurvey()
    pass

if __name__ == "main":
    main()
