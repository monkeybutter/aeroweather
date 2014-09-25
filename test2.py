from __future__ import division
import re
import datetime

MISSING_RE = re.compile(r"^[M/]+$")

DATE_RE = re.compile(r"""^(?P<year>\d\d)-
                          (?P<month>\d\d)-
                          (?P<day>\d\d)?\s+""",
                          re.VERBOSE)
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
VISIBILITY_RE =   re.compile(r"""^(?P<vis>(?P<dist>M?(\d\s+)?\d/\d\d?|M?\d+)
                                     ( \s*(?P<units>SM|KM|M|U) | NDV |
                                          (?P<dir>[NSEW][EW]?) )? |
                                    CAVOK )\s+""",
                                    re.VERBOSE)

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



metar_code = '11-01-01 METAR KATL 012052Z COR 12007KT 9999 -RA BR OVC003 15/14 A3000 '
metar = {}

# Report type
match = DATE_RE.match(metar_code)
if match:
    date = datetime.datetime(2000+int(match.group('year')), int(match.group('month')), int(match.group('day')), 0, 0)
    metar_code = metar_code[match.end():]

print(metar)

# Report type
match = TYPE_RE.match(metar_code)
if match:
    metar['type'] = match.group('type')
    metar_code = metar_code[match.end():]

print(metar)

# Airport code
match = STATION_RE.match(metar_code)
if match:
    metar['code'] = match.group('station')
    metar_code = metar_code[match.end():]

print(metar)

# Datetime
match = TIME_RE.match(metar_code)
if match:
    if date is None:
        date = datetime.datetime.now()
    metardate = datetime.datetime(date.year, date.month, int(match.group('day')), int(match.group('hour')), int(match.group('min')))
    metar['datetime'] = metardate
    metar_code = metar_code[match.end():]

print(metar)

# Modifier
match = MODIFIER_RE.match(metar_code)
if match:
    metar['mod'] = match.group('mod')
    metar_code = metar_code[match.end():]

print(metar)

# Wind
match = WIND_RE.match(metar_code)
if match:
    metar['wind'] = match.groupdict()
    metar_code = metar_code[match.end():]
else:
    metar['wind'] = None

print(metar)

# Visibility
match = VISIBILITY_RE.match(metar_code)
if match:
    print match.groupdict()
    metar['visibility'] = []
    while match:
        raw = match.groupdict()
        raw['dist'] = eval(re.sub(' ', '+', raw['dist']))
        print()
        print(raw['dist'])
        print()
        #raw['dist'] = eval(raw['dist'])
        metar['visibility'].append(raw)
        metar_code = metar_code[match.end():]
        match = VISIBILITY_RE.match(metar_code)

print(metar)

# Runway
match = RUNWAY_RE.match(metar_code)
if match:
    metar['runway'] = []
    while match:
        metar['runway'].append(match.group(0))
        metar_code = metar_code[match.end():]
        match = RUNWAY_RE.match(metar_code)

print(metar)

# Weather
match = WEATHER_RE.match(metar_code)
if match:
    metar['weather'] = []
    while match:
        metar['weather'].append(match.groupdict())
        metar_code = metar_code[match.end():]
        match = WEATHER_RE.match(metar_code)

print(metar)

# Sky
match = SKY_RE.match(metar_code)
if match:
    metar['sky'] = []
    while match:
        metar['sky'].append(match.groupdict())
        metar_code = metar_code[match.end():]
        match = SKY_RE.match(metar_code)

print(metar)

# Temperature / Dew Point
match = TEMP_RE.match(metar_code)
if match:
    s = list(match.group('temp'))
    if s[0] == 'M':
        s[0] = '-'
    metar['temperature'] = "".join(s)
    s = list(match.group('dewpt'))
    if s[0] == 'M':
        s[0] = '-'
    metar['dewpoint'] = "".join(s)
    metar_code = metar_code[match.end():]
else:
    metar['temperature'] = None
    metar['dewpoint'] = None

print(metar)
print metar_code
# Pressure
match = PRESS_RE.match(metar_code)
if match:
    metar['pressure'] = match.groupdict()
    metar_code = metar_code[match.end():]
else:
    metar['pressure'] = None

print(metar)

# Quotient
metar['quotient'] = metar_code

print(metar)