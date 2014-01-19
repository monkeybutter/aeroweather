#!/usr/bin/env python
"""
This module defines the tafor class.  A tafor object represents the weather report encoded by a single tafor code.
"""

__author__ = "Pablo Rozas-Larraondo"

__email__ = "p.rozas.larraondo@gmail.com"

__version__ = "0.1"

__LICENSE__ = """
Copyright (c) 2014, %s
All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.

Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
""" % __author__

import re
import datetime
#from Datatypes import *

## regular expressions to decode various groups of the tafor code

MISSING_RE = re.compile(r"^[M/]+$")

TYPE_RE = re.compile(r"^(?P<type>TAF)\s+")
MODIFIER_RE = re.compile(r"^(?P<mod>AUTO|AMD|COR|NIL)\s+")
STATION_RE =  re.compile(r"^(?P<station>[A-Z]{4})\s+")
TIME_RE = re.compile(r"""^(?P<day>[\d]{2})
                          (?P<hour>[\d]{2})
                          (?P<min>[\d]{2})Z?\s+""",
                          re.VERBOSE)
TIMEVALID_RE = re.compile(r"""^(?P<dayfrom>[\d]{2})
                          (?P<hourfrom>[\d]{2})/
                          (?P<dayto>[\d]{2})
                          (?P<hourto>[\d]{2})\s+""",
                          re.VERBOSE)
WIND_RE = re.compile(r"""^(?P<dir>[\d]{3}|///|VRB)
                          (?P<speed>[\d]{2}|//)
                          (G(?P<gust>(\d{1,3}|[/M]{1,3})))?
                          (?P<units>KT|KMH|MPS)?\s+""",
                          re.VERBOSE)
VISIBILITY_RE = re.compile(r"""^(?P<vis>(?P<dist>\d\d\d\d|////)
                          (?P<dir>[NSEW][EW]? | NDV)? | CAVOK )\s+""", 
                          re.VERBOSE)
WEATHER_RE = re.compile(r"""^(?P<int>(-|\+|VC)*)
                             (?P<desc>(MI|PR|BC|DR|BL|SH|TS|FZ)+)?
                             (?P<prec>(DZ|RA|SN|SG|IC|PL|GR|GS|UP|/)*)
                             (?P<obsc>BR|FG|FU|VA|DU|SA|HZ|PY)?
                             (?P<other>PO|SQ|FC|SS|DS|NSW|/+)?
                             (?P<int2>[-+])?\s+""",
                             re.VERBOSE)
SKY_RE= re.compile(r"""^(?P<cover>VV|CLR|SKC|SCK|NSC|NCD|BKN|SCT|FEW|OVC|///)
                        (?P<height>[\d]{3}|///)?
                        (?P<cloud>([A-Z][A-Z]+|///))?\s+""",
                        re.VERBOSE)

MAXTEMP_RE = re.compile(r"""^TX(?P<temp>(M|-)?[\d]{2}|//)/
                             (?P<day>[\d]{2})
                             (?P<hour>[\d]{2})Z?\s+""",
                             re.VERBOSE)

MINTEMP_RE = re.compile(r"""^TN(?P<temp>(M|-)?[\d]{2}|//)/
                             (?P<day>[\d]{2})
                             (?P<hour>[\d]{2})Z?\s+""",
                             re.VERBOSE)

CHANGES_RE = re.compile(r"""^(?P<prob>PROB[\d]{2})?
                             (?P<change>(FM[\d]{6}|BECMG|TEMPO|INTER)*)?\s+""",
                             re.VERBOSE)



class Tafor(object):
    """TAFOR (terminal aerodrome forecast)"""
  
    def __init__( self, tafor_code):
        """Parse raw tafor code."""
        self.tafor = dict()                # Tafor object containing all information
        self.tafor['raw'] = tafor_code
        tafor_code = tafor_code + ' '


        try:
            # Report type
            match = TYPE_RE.match(tafor_code)
            if match:
                self.tafor['type'] = match.group('type')
                tafor_code = tafor_code[match.end():]

            # Modifier
            match = MODIFIER_RE.match(tafor_code)
            if match:
                self.tafor['mod'] = match.group('mod')
                tafor_code = tafor_code[match.end():]

            # Airport code
            match = STATION_RE.match(tafor_code)
            if match:
                self.tafor['code'] = match.group('station')
                tafor_code = tafor_code[match.end():]

            # Datetime
            match = TIME_RE.match(tafor_code)
            if match:
                now = datetime.datetime.now()
                tafor_date = datetime.datetime(now.year, now.month, int(match.group('day')), int(match.group('hour')), int(match.group('min')))
                self.tafor['datetime'] = tafor_date
                tafor_code = tafor_code[match.end():]

            # Time valid
            match = TIMEVALID_RE.match(tafor_code)
            if match:
                validity = {}
                now = datetime.datetime.now()
                valid_from = datetime.datetime(now.year, now.month, int(match.group('dayfrom')), int(match.group('hourfrom')), 0)
                validity["from"] = valid_from
                valid_to = datetime.datetime(now.year, now.month, int(match.group('dayto')), int(match.group('hourto')), 0)
                validity["to"] = valid_to
                self.tafor['validity'] = validity
                tafor_code = tafor_code[match.end():]

            # Wind
            match = WIND_RE.match(tafor_code)
            if match:
                self.tafor['wind'] = match.groupdict()
                tafor_code = tafor_code[match.end():]

            # Visibility
            match = VISIBILITY_RE.match(tafor_code)
            if match:
                self.tafor['visibility'] = []
                while match:
                    self.tafor['visibility'].append(match.group('vis'))
                    tafor_code = tafor_code[match.end():]
                    match = VISIBILITY_RE.match(tafor_code)

            # Weather
            match = WEATHER_RE.match(tafor_code)
            if match:
                self.tafor['weather'] = []
                while match:
                    self.tafor['weather'].append(match.groupdict())
                    tafor_code = tafor_code[match.end():]
                    match = WEATHER_RE.match(tafor_code)

            # Sky
            match = SKY_RE.match(tafor_code)
            if match:
                self.tafor['sky'] = []
                while match:
                    self.tafor['sky'].append(match.groupdict())
                    tafor_code = tafor_code[match.end():]
                    match = SKY_RE.match(tafor_code)

            # Changes
            match = CHANGES_RE.match(tafor_code)
            if match:
                self.tafor['changes'] = []
                while match:
                    tafor_code = tafor_code[match.end():]
                    change = {}
                    change["modifier"] = match.groupdict()

                    # Validity
                    match_in = TIMEVALID_RE.match(tafor_code)
                    if match_in:
                        validity = {}
                        now = datetime.datetime.now()
                        valid_from = datetime.datetime(now.year, now.month, int(match_in.group('dayfrom')), int(match_in.group('hourfrom')), 0)
                        validity["from"] = valid_from
                        valid_to = datetime.datetime(now.year, now.month, int(match_in.group('dayto')), int(match_in.group('hourto')), 0)
                        validity["to"] = valid_to
                        change["validity"] = validity
                        tafor_code = tafor_code[match_in.end():]

                    # Wind
                    match_in = WIND_RE.match(tafor_code)
                    if match_in:
                        change['wind'] = match_in.groupdict()
                        tafor_code = tafor_code[match_in.end():]

                    # Visibility
                    match_in = VISIBILITY_RE.match(tafor_code)
                    if match_in:
                        change['visibility'] = []
                        while match_in:
                            change['visibility'].append(match_in.group('vis'))
                            tafor_code = tafor_code[match_in.end():]
                            match_in = VISIBILITY_RE.match(tafor_code)

                    # Weather
                    match_in = WEATHER_RE.match(tafor_code)
                    if match_in:
                        change['weather'] = []
                        while match_in:
                            change['weather'].append(match_in.groupdict())
                            tafor_code = tafor_code[match_in.end():]
                            match_in = WEATHER_RE.match(tafor_code)

                    # Sky
                    match_in = SKY_RE.match(tafor_code)
                    if match_in:
                        change['sky'] = []
                        while match_in:
                            change['sky'].append(match_in.groupdict())
                            tafor_code = tafor_code[match_in.end():]
                            match_in = SKY_RE.match(tafor_code)

                    self.tafor['changes'].append(change)
                    match = CHANGES_RE.match(tafor_code)


            # Quotient
            self.tafor['quotient'] = tafor_code

        except Exception, err:
            pass