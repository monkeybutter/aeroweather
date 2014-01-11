#!/usr/bin/env python
#
#  A python package for interpreting METAR and SPECI weather reports.
#  
#  US conventions for METAR/SPECI reports are described in chapter 12 of
#  the Federal Meteorological Handbook No.1. (FMH-1 1995), issued by NOAA. 
#  See <http://metar.noaa.gov/>
# 
#  International conventions for the METAR and SPECI codes are specified in 
#  the WMO Manual on Codes, vol I.1, Part A (WMO-306 I.i.A).  
#
#  This module handles a reports that follow the US conventions, as well
#  the more general encodings in the WMO spec.  Other regional conventions
#  are not supported at present.
#
#  The current METAR report for a given station is available at the URL
#  http://weather.noaa.gov/pub/data/observations/metar/stations/<station>.TXT
#  where <station> is the four-letter ICAO station code.  
#
#  The METAR reports for all reporting stations for any "cycle" (i.e., hour) 
#  in the last 24 hours is available in a single file at the URL
#  http://weather.noaa.gov/pub/data/observations/metar/cycles/<cycle>Z.TXT
#  where <cycle> is a 2-digit cycle number (e.g., "00", "05" or "23").  
# 
#  Copyright 2004  Tom Pollard
# 
"""
This module defines the Metar class.  A Metar object represents the weather report encoded by a single METAR code.
"""

__author__ = "Pablo Rozas-Larraondo"

__email__ = "p.rozas.larraondo@gmail.com"

__version__ = "0.1"

__LICENSE__ = """
Copyright (c) 2013, %s
All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.

Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
""" % __author__

import re
import datetime

## regular expressions to decode various groups of the METAR code

MISSING_RE = re.compile(r"^[M/]+$")

TYPE_RE = re.compile(r"^(?P<type>METAR|SPECI)?\s+")
STATION_RE = re.compile(r"^(?P<station>[A-Z][A-Z0-9]{3})\s+")
TIME_RE = re.compile(r"""^(?P<day>\d\d)
                          (?P<hour>\d\d)
                          (?P<min>\d\d)Z?\s+""",
                          re.VERBOSE)
MODIFIER_RE = re.compile(r"^(?P<mod>AUTO|FINO|NIL|TEST|CORR?|RTD|CC[A-G])\s+")
WIND_RE = re.compile(r"""^(?P<dir>[\dO]{3}|[0O]|///|MMM|VRB)
                          (?P<speed>P?[\dO]{2,3}|[0O]+|[/M]{2,3})
                        (G(?P<gust>P?(\d{1,3}|[/M]{1,3})))?
                          (?P<units>KTS?|LT|K|T|KMH|MPS)?
                      (\s+(?P<varfrom>\d\d\d)V
                          (?P<varto>\d\d\d))?\s+""",
                          re.VERBOSE)
# VISIBILITY_RE =   re.compile(r"""^(?P<vis>(?P<dist>M?(\d\s+)?\d/\d\d?|M?\d+)
#                                     ( \s*(?P<units>SM|KM|M|U) | NDV |
#                                          (?P<dir>[NSEW][EW]?) )? |
#                                    CAVOK )\s+""",
#                                    re.VERBOSE)
# start patch

VISIBILITY_RE = re.compile(r"""^(?P<vis>(?P<dist>\d\d\d\d|////)
                          (?P<dir>[NSEW][EW]? | NDV)? | CAVOK )\s+""", 
                          re.VERBOSE)

# end patch
RUNWAY_RE = re.compile(r"""^(RVRNO | 
                             R(?P<name>\d\d(RR?|LL?|C)?)/
                              (?P<low>(M|P)?\d\d\d\d)
                            (V(?P<high>(M|P)?\d\d\d\d))?
                              (?P<unit>FT)?[/NDU]*)\s+""",
                              re.VERBOSE)
WEATHER_RE = re.compile(r"""^(?P<int>(-|\+|VC)*)
                             (?P<desc>(MI|PR|BC|DR|BL|SH|TS|FZ)+)?
                             (?P<prec>(DZ|RA|SN|SG|IC|PL|GR|GS|UP|/)*)
                             (?P<obsc>BR|FG|FU|VA|DU|SA|HZ|PY)?
                             (?P<other>PO|SQ|FC|SS|DS|NSW|/+)?
                             (?P<int2>[-+])?\s+""",
                             re.VERBOSE)
SKY_RE= re.compile(r"""^(?P<cover>VV|CLR|SKC|SCK|NSC|NCD|BKN|SCT|FEW|OVC|///)
                        (?P<height>[\dO]{2,4}|///)?
                        (?P<cloud>([A-Z][A-Z]+|///))?\s+""",
                        re.VERBOSE)
TEMP_RE = re.compile(r"""^(?P<temp>(M|-)?\d+|//|XX|MM)/
                          (?P<dewpt>(M|-)?\d+|//|XX|MM)?\s+""",
                          re.VERBOSE)
PRESS_RE = re.compile(r"""^(?P<unit>A|Q|QNH|SLP)?
                           (?P<press>[\dO]{3,4}|////)
                           (?P<unit2>INS)?\s+""",
                           re.VERBOSE)
RECENT_RE = re.compile(r"""^RE(?P<desc>MI|PR|BC|DR|BL|SH|TS|FZ)?
                              (?P<prec>(DZ|RA|SN|SG|IC|PL|GR|GS|UP)*)?
                              (?P<obsc>BR|FG|FU|VA|DU|SA|HZ|PY)?
                              (?P<other>PO|SQ|FC|SS|DS)?\s+""",
                              re.VERBOSE)
WINDSHEAR_RE = re.compile(r"^(WS\s+)?(ALL\s+RWY|RWY(?P<name>\d\d(RR?|L?|C)?))\s+")
COLOR_RE = re.compile(r"""^(BLACK)?(BLU|GRN|WHT|RED)\+?
                        (/?(BLACK)?(BLU|GRN|WHT|RED)\+?)*\s*""",
                        re.VERBOSE)
RUNWAYSTATE_RE = re.compile(r"""((?P<name>\d\d) |
                                 R(?P<namenew>\d\d)(RR?|LL?|C)?/?)
                                (?P<deposit>(\d|/))
                                (?P<extent>(\d|/))
                                (?P<depth>(\d\d|//))
                                (?P<friction>(\d\d|//))\s+""",
                             re.VERBOSE)
TREND_RE = re.compile(r"^(?P<trend>TEMPO|BECMG|FCST|NOSIG)\s+")

TRENDTIME_RE = re.compile(r"(?P<when>(FM|TL|AT))(?P<hour>\d\d)(?P<min>\d\d)\s+")

REMARK_RE = re.compile(r"^(RMKS?|NOSPECI|NOSIG)\s+")

## regular expressions for remark groups

AUTO_RE = re.compile(r"^AO(?P<type>\d)\s+")
SEALVL_PRESS_RE = re.compile(r"^SLP(?P<press>\d\d\d)\s+")
PEAK_WIND_RE = re.compile(r"""^P[A-Z]\s+WND\s+
                               (?P<dir>\d\d\d)
                               (?P<speed>P?\d\d\d?)/
                               (?P<hour>\d\d)?
                               (?P<min>\d\d)\s+""",
                               re.VERBOSE)
WIND_SHIFT_RE = re.compile(r"""^WSHFT\s+
                                (?P<hour>\d\d)?
                                (?P<min>\d\d)
                                (\s+(?P<front>FROPA))?\s+""",
                                re.VERBOSE)
PRECIP_1HR_RE = re.compile(r"^P(?P<precip>\d\d\d\d)\s+")
PRECIP_24HR_RE = re.compile(r"""^(?P<type>6|7)
                                 (?P<precip>\d\d\d\d)\s+""",
                                 re.VERBOSE)
PRESS_3HR_RE = re.compile(r"""^5(?P<tend>[0-8])
                                (?P<press>\d\d\d)\s+""",
                                re.VERBOSE)
TEMP_1HR_RE = re.compile(r"""^T(?P<tsign>0|1)
                               (?P<temp>\d\d\d)
                               ((?P<dsign>0|1)
                               (?P<dewpt>\d\d\d))?\s+""",
                               re.VERBOSE)
TEMP_6HR_RE = re.compile(r"""^(?P<type>1|2)
                              (?P<sign>0|1)
                              (?P<temp>\d\d\d)\s+""",
                              re.VERBOSE)
TEMP_24HR_RE = re.compile(r"""^4(?P<smaxt>0|1)
                                (?P<maxt>\d\d\d)
                                (?P<smint>0|1)
                                (?P<mint>\d\d\d)\s+""",
                                re.VERBOSE)
UNPARSED_RE = re.compile(r"(?P<group>\S+)\s+")

LIGHTNING_RE = re.compile(r"""^((?P<freq>OCNL|FRQ|CONS)\s+)?
                             LTG(?P<type>(IC|CC|CG|CA)*)
                                ( \s+(?P<loc>( OHD | VC | DSNT\s+ | \s+AND\s+ | 
                                 [NSEW][EW]? (-[NSEW][EW]?)* )+) )?\s+""",
                                re.VERBOSE)
                                                  
TS_LOC_RE = re.compile(r"""TS(\s+(?P<loc>( OHD | VC | DSNT\s+ | \s+AND\s+ | 
                                           [NSEW][EW]? (-[NSEW][EW]?)* )+))?
                                          ( \s+MOV\s+(?P<dir>[NSEW][EW]?) )?\s+""",
                           re.VERBOSE)
      
## METAR report objects


class Metar(object):
  """METAR (aviation meteorology report)"""
  
  def __init__( self, metarcode):
      """Parse raw METAR code."""
      self.metar = dict()                # Metar object containing all information
      self.metar['raw'] = metarcode
      
      try:
        # Report type
        match = TYPE_RE.match(metarcode)
        if match:
          self.metar['type'] = match.group('type') 
          metarcode = metarcode[match.end():]

        # Airport code
        match = STATION_RE.match(metarcode)
        if match:
          self.metar['code'] = match.group('station') 
          metarcode = metarcode[match.end():]

        # Datetime
        match = TIME_RE.match(metarcode)
        if match:
          now = datetime.datetime.now()
          metardate = datetime.datetime(now.year, now.month, int(match.group('day')), int(match.group('hour')), int(match.group('min')))
          self.metar['datetime'] = metardate.isoformat('T')
          metarcode = metarcode[match.end():]

        # Modifier
        match = MODIFIER_RE.match(metarcode)
        if match:
          self.metar['datetime'] = match.group('mod') 
          metarcode = metarcode[match.end():]

        # Wind
        match = WIND_RE.match(metarcode)
        if match:
          self.metar['wind'] = match.groupdict()
          metarcode = metarcode[match.end():]

        # Visibility
        match = VISIBILITY_RE.match(metarcode)
        if match:
          self.metar['visibility'] = []
          while match:
            self.metar['visibility'].append(match.group('vis'))
            metarcode = metarcode[match.end():]
            match = VISIBILITY_RE.match(metarcode)

        # Runway
        match = RUNWAY_RE.match(metarcode)
        if match:
          self.metar['runway'] = []
          while match:
            print(match.group(0))
            self.metar['runway'].append(match.group(0))
            metarcode = metarcode[match.end():]
            match = RUNWAY_RE.match(metarcode)

        # Weather
        match = WEATHER_RE.match(metarcode)
        if match:
          self.metar['weather'] = []
          while match:
            self.metar['weather'].append(match.groupdict())
            metarcode = metarcode[match.end():]
            match = WEATHER_RE.match(metarcode)

        # Sky
        match = SKY_RE.match(metarcode)
        if match:
          self.metar['sky'] = []
          while match:
            self.metar['sky'].append(match.groupdict())
            metarcode = metarcode[match.end():]
            match = SKY_RE.match(metarcode)

        # Temperature / Dew Point
        match = TEMP_RE.match(metarcode)
        if match:
          self.metar['temperature'] = match.group('temp') 
          self.metar['dewpoint'] = match.group('dewpt') 
          metarcode = metarcode[match.end():]

        # Pressure
        match = PRESS_RE.match(metarcode)
        if match:
          self.metar['pressure'] = match.group('press') 
          metarcode = metarcode[match.end():]
          
        # Quotient
        self.metar['quotient'] = metarcode

      except Exception, err:
        pass
